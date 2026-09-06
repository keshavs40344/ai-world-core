"""
Multi-Department Dynamic Task Delegation Engine (department_orchestrator.py)
============================================================================
Scalable, decentralized multi-department task orchestration built strictly with
native Python (Asyncio/Queue) and SQLAlchemy.

Key Architectural Components:
1. Department-Level Task Routing:
   - 4 Departments: Product, Engineering, QA, and Operations.
   - Strict Task status transitions: PENDING -> IN_PROGRESS -> BLOCKED -> COMPLETED -> FAILED.
   - CTO / Governor Goal Decomposition into sequential departmental sub-tasks.
2. Dynamic Agent Factory (No Agent Explosion):
   - On-demand provisioning with role, department, token budgets, and status.
   - Hard Guardrails: MAX_CONCURRENT_AGENTS (max 10 globally) and MAX_AGENT_LIFETIME_TASKS.
   - Recycles or terminates idle/exhausted agents cleanly.
3. Inter-Department Hand-off Protocol:
   - Strict Pydantic contracts:
     * Product: PRDSchema
     * Engineering: CodeArtifactSchema
     * QA: TestReportSchema
     * Operations: DeploymentManifestSchema
   - Automatic backward routing from QA to Engineering on test failures with retry cap (max 2 retries).
4. Real-Time Non-Blocking Event Loop:
   - Asynchronous dependency evaluation via asyncio.
   - Departmental cost & token accounting tracked to SQLite database.
"""

import os
import sys
import time
import uuid
import socket
import signal
import asyncio
import logging
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone

from pydantic import BaseModel, Field
from sqlalchemy import (
    String, Float, Integer, Boolean, Text, DateTime,
    ForeignKey, create_engine, desc
)
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column, relationship,
    sessionmaker, Session
)

# Windows UTF-8 stdout configuration
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ------------------------------------------------------------------------------
# Logging Setup
# ------------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("DepartmentOrchestrator")

# ------------------------------------------------------------------------------
# Database & ORM Definitions
# ------------------------------------------------------------------------------
DB_URL = "sqlite:///orchestrator_departments.db"

class Base(DeclarativeBase):
    pass

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED = "BLOCKED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class DepartmentType(str, Enum):
    PRODUCT = "Product"
    ENGINEERING = "Engineering"
    QA = "QA"
    OPERATIONS = "Operations"

class AgentStatus(str, Enum):
    IDLE = "idle"
    BUSY = "busy"
    TERMINATED = "terminated"

class DBDepartmentTask(Base):
    __tablename__ = "dept_tasks"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    goal_id: Mapped[str] = mapped_column(String(64), index=True)
    department: Mapped[str] = mapped_column(String(32))
    name: Mapped[str] = mapped_column(String(128))
    status: Mapped[str] = mapped_column(String(32), default=TaskStatus.PENDING.value)
    prerequisite_task_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    assigned_agent_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    input_payload_json: Mapped[str] = mapped_column(Text, default="{}")
    output_payload_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    cost_usd: Mapped[float] = mapped_column(Float, default=0.0)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

class DBAgentRecord(Base):
    __tablename__ = "dept_agents"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    role: Mapped[str] = mapped_column(String(64))
    department: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(32), default=AgentStatus.IDLE.value)
    lifetime_tasks: Mapped[int] = mapped_column(Integer, default=0)
    max_token_budget: Mapped[int] = mapped_column(Integer, default=50000)
    tokens_consumed: Mapped[int] = mapped_column(Integer, default=0)
    total_cost_usd: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

class DBAuditEntry(Base):
    __tablename__ = "dept_audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    department: Mapped[str] = mapped_column(String(32))
    agent_id: Mapped[str] = mapped_column(String(64))
    action: Mapped[str] = mapped_column(String(64))
    details: Mapped[str] = mapped_column(Text)
    cost_usd: Mapped[float] = mapped_column(Float, default=0.0)

engine = create_engine(DB_URL, echo=False)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

# ------------------------------------------------------------------------------
# Inter-Department Hand-off Protocol (Pydantic Schemas)
# ------------------------------------------------------------------------------
class PRDSchema(BaseModel):
    feature_title: str
    target_problem: str
    target_users: str
    functional_requirements: List[str]
    api_contracts: List[Dict[str, Any]]
    success_metrics: str

class CodeArtifactSchema(BaseModel):
    service_name: str
    version: str
    source_files: Dict[str, str]  # file_path -> content
    entrypoint: str
    dependencies: List[str]

class TestReportSchema(BaseModel):
    service_name: str
    version: str
    total_tests: int
    tests_passed: int
    tests_failed: int
    passed: bool
    failure_logs: Optional[str] = None
    execution_duration_sec: float

class DeploymentManifestSchema(BaseModel):
    service_name: str
    version: str
    assigned_port: int
    process_pid: int
    health_url: str
    environment: str = "production"
    status: str = "LIVE"

# ------------------------------------------------------------------------------
# Dynamic Agent Factory (Guarded by Concurrency Caps & Lifetimes)
# ------------------------------------------------------------------------------
MAX_CONCURRENT_AGENTS = 10
MAX_AGENT_LIFETIME_TASKS = 5

class AgentInstance:
    def __init__(self, agent_id: str, role: str, department: DepartmentType, max_token_budget: int = 50000):
        self.agent_id = agent_id
        self.role = role
        self.department = department
        self.max_token_budget = max_token_budget
        self.tokens_consumed = 0
        self.total_cost_usd = 0.0
        self.lifetime_tasks = 0
        self.status = AgentStatus.IDLE

    def can_accept_task(self) -> bool:
        if self.status != AgentStatus.IDLE:
            return False
        if self.lifetime_tasks >= MAX_AGENT_LIFETIME_TASKS:
            return False
        if self.tokens_consumed >= self.max_token_budget:
            return False
        return True

    def record_usage(self, tokens: int, cost_usd: float):
        self.tokens_consumed += tokens
        self.total_cost_usd += cost_usd
        self.lifetime_tasks += 1
        if self.lifetime_tasks >= MAX_AGENT_LIFETIME_TASKS:
            self.status = AgentStatus.TERMINATED
            logger.info(f"Agent {self.agent_id} reached MAX_AGENT_LIFETIME_TASKS ({MAX_AGENT_LIFETIME_TASKS}). Terminated.")
        else:
            self.status = AgentStatus.IDLE

class AgentFactory:
    def __init__(self):
        self.active_agents: Dict[str, AgentInstance] = {}
        self._lock = asyncio.Lock()

    async def get_or_provision_agent(self, department: DepartmentType, role: str) -> AgentInstance:
        async with self._lock:
            # 1. Look for existing idle agent in this department
            for agent in self.active_agents.values():
                if agent.department == department and agent.role == role and agent.can_accept_task():
                    agent.status = AgentStatus.BUSY
                    return agent

            # 2. Check active concurrent agent limit
            active_count = sum(1 for a in self.active_agents.values() if a.status != AgentStatus.TERMINATED)
            if active_count >= MAX_CONCURRENT_AGENTS:
                # Terminate any idle agent to free a slot
                for a_id, a in list(self.active_agents.items()):
                    if a.status == AgentStatus.IDLE:
                        a.status = AgentStatus.TERMINATED
                        del self.active_agents[a_id]
                        logger.warning(f"Reclaimed agent slot: Terminated idle agent {a_id}")
                        break
                else:
                    raise RuntimeError(f"Hard Guardrail Violation: MAX_CONCURRENT_AGENTS ({MAX_CONCURRENT_AGENTS}) exceeded!")

            # 3. Provision new agent on demand
            new_id = f"AGT-{department.value.upper()[:4]}-{uuid.uuid4().hex[:6].upper()}"
            agent = AgentInstance(agent_id=new_id, role=role, department=department)
            agent.status = AgentStatus.BUSY
            self.active_agents[new_id] = agent
            logger.info(f"Provisioned on-demand Agent: {new_id} ({role} in {department.value})")

            # Persist to DB
            with SessionLocal() as db:
                db_agent = DBAgentRecord(
                    id=agent.agent_id,
                    role=agent.role,
                    department=agent.department.value,
                    status=agent.status.value,
                    lifetime_tasks=agent.lifetime_tasks,
                    max_token_budget=agent.max_token_budget,
                    tokens_consumed=agent.tokens_consumed,
                    total_cost_usd=agent.total_cost_usd
                )
                db.add(db_agent)
                db.commit()

            return agent

    async def release_agent(self, agent: AgentInstance, tokens: int, cost: float):
        async with self._lock:
            agent.record_usage(tokens, cost)
            with SessionLocal() as db:
                db_agent = db.query(DBAgentRecord).filter_by(id=agent.agent_id).first()
                if db_agent:
                    db_agent.lifetime_tasks = agent.lifetime_tasks
                    db_agent.tokens_consumed = agent.tokens_consumed
                    db_agent.total_cost_usd = agent.total_cost_usd
                    db_agent.status = agent.status.value
                    db.commit()

# ------------------------------------------------------------------------------
# Department Queue & Real-Time Event Loop
# ------------------------------------------------------------------------------
class DepartmentQueue:
    def __init__(self, factory: AgentFactory):
        self.factory = factory
        self.queue: asyncio.Queue = asyncio.Queue()
        self.running = True
        self.task_registry: Dict[str, DBDepartmentTask] = {}
        self._lock = asyncio.Lock()

    async def enqueue_task(self, task: DBDepartmentTask):
        async with self._lock:
            self.task_registry[task.id] = task
        await self.queue.put(task)
        logger.info(f"Enqueued Task [{task.department}]: {task.name} ({task.id})")

    async def _re_enqueue_later(self, task: DBDepartmentTask, delay: float = 0.5):
        await asyncio.sleep(delay)
        await self.queue.put(task)

    async def process_task(self, task: DBDepartmentTask):
        with SessionLocal() as db:
            # Check prerequisite
            if task.prerequisite_task_id:
                prereq = db.query(DBDepartmentTask).filter_by(id=task.prerequisite_task_id).first()
                if prereq and prereq.status != TaskStatus.COMPLETED.value:
                    task.status = TaskStatus.BLOCKED.value
                    db.query(DBDepartmentTask).filter_by(id=task.id).update({"status": TaskStatus.BLOCKED.value})
                    db.commit()
                    logger.warning(f"Task {task.id} is BLOCKED: Waiting on prerequisite {task.prerequisite_task_id}")
                    # Release current queue slot, wait asynchronously, then re-enqueue
                    asyncio.create_task(self._re_enqueue_later(task))
                    return

            # Mark in progress
            task.status = TaskStatus.IN_PROGRESS.value
            db.query(DBDepartmentTask).filter_by(id=task.id).update({"status": TaskStatus.IN_PROGRESS.value})
            db.commit()

        dept = DepartmentType(task.department)
        role_map = {
            DepartmentType.PRODUCT: "Technical Product Manager",
            DepartmentType.ENGINEERING: "Senior Software Engineer",
            DepartmentType.QA: "Lead QA Automation Engineer",
            DepartmentType.OPERATIONS: "Site Reliability Engineer"
        }

        # Provision specialist agent
        agent = await self.factory.get_or_provision_agent(dept, role_map[dept])
        logger.info(f"Agent {agent.agent_id} assigned to Task {task.id} in {dept.value}")

        # Execute departmental handler
        output_payload, tokens, cost = await self._dispatch_department_work(dept, task, agent)

        # Audit and update task
        with SessionLocal() as db:
            db_task = db.query(DBDepartmentTask).filter_by(id=task.id).first()
            db_task.assigned_agent_id = agent.agent_id
            db_task.tokens_used = tokens
            db_task.cost_usd = cost
            db_task.completed_at = datetime.now(timezone.utc)

            # Check for backward routing on QA failure
            if dept == DepartmentType.QA:
                report = TestReportSchema.model_validate_json(output_payload)
                if not report.passed:
                    if db_task.retry_count < 2:
                        db_task.status = TaskStatus.FAILED.value
                        db_task.retry_count += 1
                        db.commit()
                        logger.warning(
                            f"QA Validation FAILED for {task.id}. Backward routing to Engineering "
                            f"(Retry {db_task.retry_count}/2)..."
                        )
                        # Re-route to Engineering
                        await self._reroute_to_engineering(db_task, report.failure_logs or "Assertion failed")
                        await self.factory.release_agent(agent, tokens, cost)
                        return
                    else:
                        logger.error(f"Task {task.id} exceeded max retries (2). Aborting workflow.")
                        db_task.status = TaskStatus.FAILED.value
                        db.commit()
                        await self.factory.release_agent(agent, tokens, cost)
                        return

            db_task.status = TaskStatus.COMPLETED.value
            db_task.output_payload_json = output_payload
            db.commit()

            # Record audit log
            audit = DBAuditEntry(
                department=dept.value,
                agent_id=agent.agent_id,
                action=f"{dept.value.upper()}_HANDOFF",
                details=f"Completed task '{task.name}' ({task.id})",
                cost_usd=cost
            )
            db.add(audit)
            db.commit()

        await self.factory.release_agent(agent, tokens, cost)
        logger.info(f"Task {task.id} COMPLETED by {agent.agent_id} (Cost: ${cost:.4f}, Tokens: {tokens})")

    async def _reroute_to_engineering(self, failed_task: DBDepartmentTask, failure_log: str):
        """Routes backward from QA to Engineering with failure logs attached."""
        with SessionLocal() as db:
            new_task_id = f"TASK-ENG-RETRY-{uuid.uuid4().hex[:6].upper()}"
            eng_task = DBDepartmentTask(
                id=new_task_id,
                goal_id=failed_task.goal_id,
                department=DepartmentType.ENGINEERING.value,
                name="Engineering Patch & Bugfix (Post-QA Failure)",
                status=TaskStatus.PENDING.value,
                prerequisite_task_id=None,
                input_payload_json=f'{{"failure_log": "{failure_log}"}}',
                retry_count=failed_task.retry_count
            )
            db.add(eng_task)
            db.commit()
            logger.info(f"Backward routing successful: Created Engineering Patch Task {new_task_id}")
            await self.queue.put(eng_task)

    async def _dispatch_department_work(
        self,
        dept: DepartmentType,
        task: DBDepartmentTask,
        agent: AgentInstance
    ) -> Tuple[str, int, float]:
        """Simulates departmental processing conforming to strict Pydantic schemas."""
        await asyncio.sleep(0.3)

        if dept == DepartmentType.PRODUCT:
            prd = PRDSchema(
                feature_title="Decentralized Dynamic URL Routing Engine",
                target_problem="High-throughput redirection with collision-resistant hashing and custom slugs",
                target_users="Enterprise API Gateways & Developers",
                functional_requirements=[
                    "Sub-millisecond redirect lookups",
                    "Atomic quota allocation",
                    "Vanity slug reservation"
                ],
                api_contracts=[
                    {"endpoint": "/v1/links", "method": "POST", "response_code": 201},
                    {"endpoint": "/{slug}", "method": "GET", "response_code": 302}
                ],
                success_metrics="p99 latency < 5ms under 10k RPS"
            )
            return prd.model_dump_json(), 650, 0.013

        elif dept == DepartmentType.ENGINEERING:
            code_art = CodeArtifactSchema(
                service_name="DynamicRoutingEngine",
                version="1.0.0",
                source_files={
                    "main.py": "from fastapi import FastAPI\napp = FastAPI()\n@app.get('/health')\ndef h(): return {'ok': True}",
                    "test_main.py": "def test_h(): assert True"
                },
                entrypoint="main.py",
                dependencies=["fastapi", "uvicorn", "pydantic"]
            )
            return code_art.model_dump_json(), 1450, 0.029

        elif dept == DepartmentType.QA:
            # QA automated test execution
            report = TestReportSchema(
                service_name="DynamicRoutingEngine",
                version="1.0.0",
                total_tests=12,
                tests_passed=12,
                tests_failed=0,
                passed=True,
                failure_logs=None,
                execution_duration_sec=0.45
            )
            return report.model_dump_json(), 800, 0.016

        elif dept == DepartmentType.OPERATIONS:
            manifest = DeploymentManifestSchema(
                service_name="DynamicRoutingEngine",
                version="1.0.0",
                assigned_port=8088,
                process_pid=18442,
                health_url="http://127.0.0.1:8088/health",
                environment="production",
                status="LIVE"
            )
            return manifest.model_dump_json(), 500, 0.010

        return "{}", 100, 0.002

    async def run_worker_loop(self):
        logger.info("Department Queue Worker Loop started (non-blocking).")
        while self.running:
            try:
                task = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                await self.process_task(task)
                self.queue.task_done()
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Worker Loop Error: {e}", exc_info=True)

# ------------------------------------------------------------------------------
# CTO / World Governor Goal Decomposition
# ------------------------------------------------------------------------------
class WorldGovernor:
    def __init__(self, queue: DepartmentQueue):
        self.queue = queue

    async def decompose_and_dispatch_goal(self, goal_title: str) -> str:
        goal_id = f"GOAL-{uuid.uuid4().hex[:8].upper()}"
        logger.info(f"CTO/Governor decomposing High-Level Goal: '{goal_title}' ({goal_id})")

        with SessionLocal() as db:
            # Step 1: Product PRD
            t_prd_id = f"TASK-PRD-{uuid.uuid4().hex[:6].upper()}"
            t_prd = DBDepartmentTask(
                id=t_prd_id,
                goal_id=goal_id,
                department=DepartmentType.PRODUCT.value,
                name="Synthesize Product Requirement Document (PRD)",
                status=TaskStatus.PENDING.value,
                prerequisite_task_id=None
            )

            # Step 2: Engineering Implementation
            t_eng_id = f"TASK-ENG-{uuid.uuid4().hex[:6].upper()}"
            t_eng = DBDepartmentTask(
                id=t_eng_id,
                goal_id=goal_id,
                department=DepartmentType.ENGINEERING.value,
                name="Synthesize Service Implementation & Test Suite",
                status=TaskStatus.PENDING.value,
                prerequisite_task_id=t_prd_id
            )

            # Step 3: QA Validation
            t_qa_id = f"TASK-QA-{uuid.uuid4().hex[:6].upper()}"
            t_qa = DBDepartmentTask(
                id=t_qa_id,
                goal_id=goal_id,
                department=DepartmentType.QA.value,
                name="Automated Sandbox Test Execution & Quality Audit",
                status=TaskStatus.PENDING.value,
                prerequisite_task_id=t_eng_id
            )

            # Step 4: Operations Deployment
            t_ops_id = f"TASK-OPS-{uuid.uuid4().hex[:6].upper()}"
            t_ops = DBDepartmentTask(
                id=t_ops_id,
                goal_id=goal_id,
                department=DepartmentType.OPERATIONS.value,
                name="Controlled Dynamic Port Deployment & Live Manifest",
                status=TaskStatus.PENDING.value,
                prerequisite_task_id=t_qa_id
            )

            db.add_all([t_prd, t_eng, t_qa, t_ops])
            db.commit()

        # Enqueue in topological order
        await self.queue.enqueue_task(t_prd)
        await self.queue.enqueue_task(t_eng)
        await self.queue.enqueue_task(t_qa)
        await self.queue.enqueue_task(t_ops)

        return goal_id

# ------------------------------------------------------------------------------
# Main Async Runner & Observability Summary
# ------------------------------------------------------------------------------
async def run_orchestration_cycle():
    print("\n" + "=" * 80)
    print(" 🏛️ MULTI-DEPARTMENT DYNAMIC TASK DELEGATION ENGINE")
    print("=" * 80)

    factory = AgentFactory()
    queue = DepartmentQueue(factory)
    governor = WorldGovernor(queue)

    # Launch background consumer worker
    worker_task = asyncio.create_task(queue.run_worker_loop())

    # Dispatch High-Level Goal
    goal = "Build a high-performance, fault-tolerant Dynamic URL Routing & Link Redirection Gateway"
    goal_id = await governor.decompose_and_dispatch_goal(goal)

    # Wait for queue to drain
    print("\n[*] Real-Time Non-Blocking Event Loop processing departmental pipeline...")
    await asyncio.sleep(4.0)
    await queue.queue.join()

    # Gracefully stop worker
    queue.running = False
    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        pass

    # Print Departmental Summary & Cost Accounting
    with SessionLocal() as db:
        tasks = db.query(DBDepartmentTask).filter_by(goal_id=goal_id).all()
        agents = db.query(DBAgentRecord).all()
        audits = db.query(DBAuditEntry).order_by(DBAuditEntry.id.asc()).all()

        print("\n" + "=" * 80)
        print(" 📋 DEPARTMENTAL TASK EXECUTION & HAND-OFF TRACE")
        print("=" * 80)
        for t in tasks:
            print(f"  [{t.status:11}] [{t.department:11}] {t.name[:45]:45} | Agent: {t.assigned_agent_id or 'NONE'} | Cost: ${t.cost_usd:.4f}")

        # Cost Accounting Per Department
        dept_costs: Dict[str, float] = {}
        dept_tokens: Dict[str, int] = {}
        for t in tasks:
            dept_costs[t.department] = dept_costs.get(t.department, 0.0) + t.cost_usd
            dept_tokens[t.department] = dept_tokens.get(t.department, 0) + t.tokens_used

        print("-" * 80)
        print(" 💰 DEPARTMENT COST & TOKEN ACCOUNTING")
        print("-" * 80)
        total_cost = 0.0
        total_tokens = 0
        for d, c in dept_costs.items():
            tok = dept_tokens.get(d, 0)
            total_cost += c
            total_tokens += tok
            print(f"   Department: {d:12} | Tokens: {tok:6,d} | Cost: ${c:.4f}")

        print("-" * 80)
        print(f"   TOTAL COMPUTATION   | Tokens: {total_tokens:6,d} | Cost: ${total_cost:.4f}")
        print("-" * 80)

        print("\n 👥 AGENT FACTORY CONCURRENCY & LIFETIME METRICS")
        print(f"   Total Agents Provisioned : {len(agents)} (Hard Cap: {MAX_CONCURRENT_AGENTS})")
        for a in agents:
            print(f"   - {a.id} ({a.role}) | Dept: {a.department:11} | Tasks Run: {a.lifetime_tasks}/{MAX_AGENT_LIFETIME_TASKS} | Status: {a.status}")

        print("\n 📜 INTER-DEPARTMENT AUDIT LOGS")
        for log in audits[-6:]:
            print(f"   [{log.department:11}] [{log.agent_id:18}] -> {log.action} | {log.details}")

    print("=" * 80)
    print(" ✅ MULTI-DEPARTMENT ORCHESTRATION CYCLE COMPLETED SUCCESSFULLY")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    asyncio.run(run_orchestration_cycle())

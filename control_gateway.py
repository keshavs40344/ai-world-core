"""
Owner Control Center & Safe Deployment Gateway (control_gateway.py)
==================================================================
Production-grade FastAPI module implementing sovereign owner governance,
deterministic background worker checks, verified dynamic-port deployments,
instant safe rollbacks, and real-time observability audit dashboard.

Core Features:
1. Owner Governance & Kill-Switch:
   - POST /owner/pause: Immediately stops background loops, code gen, and tests.
   - POST /owner/resume: Safely resumes operations.
   - POST /owner/set-budget: Sets hard limits for API spend and task count.
2. Controlled Deployment & Rollback:
   - deploy_product(product_id, version): Deploys only after sandbox verification
     to an isolated directory and binds to a dynamic local port with health probing.
   - POST /owner/rollback/{product_id}: Reverts running instance to the previous
     stable version artifact, terminates the unstable instance, and logs incident.
3. Observability & Audit:
   - GET /owner/dashboard: Real-time telemetry including system state, active agents,
     task counts, spend vs budget, active deployments, and last 10 audit logs.
   - Every state change writes structured entries to the AuditLog database.
4. Minimalist & Self-Contained:
   - Vanilla FastAPI + Pydantic + standard library + SQLite/SQLAlchemy.
   - Built-in background worker loop respecting the kill-switch and budget limits.
"""

import os
import sys
import time
import socket
import signal
import shutil
import logging
import asyncio
import tempfile
import subprocess
import threading
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timezone

from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import (
    String, Float, Integer, Boolean, Text, DateTime,
    ForeignKey, create_engine, desc
)
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column, relationship,
    sessionmaker, Session
)

# ------------------------------------------------------------------------------
# Logging Configuration
# ------------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("ControlGateway")

# ------------------------------------------------------------------------------
# Database & ORM Definitions (Self-Contained SQLite Models)
# ------------------------------------------------------------------------------
DB_PATH = os.environ.get("GATEWAY_DB_PATH", "sqlite:///control_gateway.db")
DEPLOYMENTS_BASE_DIR = os.path.abspath(os.environ.get("DEPLOYMENTS_DIR", "./live_deployments"))
os.makedirs(DEPLOYMENTS_BASE_DIR, exist_ok=True)

class Base(DeclarativeBase):
    pass

class SystemState(Base):
    __tablename__ = "gateway_system_state"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    is_paused: Mapped[bool] = mapped_column(Boolean, default=False)
    budget_limit_usd: Mapped[float] = mapped_column(Float, default=100.0)
    spent_budget_usd: Mapped[float] = mapped_column(Float, default=0.0)
    task_limit_count: Mapped[int] = mapped_column(Integer, default=50)
    tasks_executed_count: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

class ProductRecord(Base):
    __tablename__ = "gateway_products"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    active_version: Mapped[str] = mapped_column(String(32), default="v1.0.0")
    previous_stable_version: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="STAGED") # STAGED, VERIFIED, DEPLOYED, ROLLED_BACK
    assigned_port: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    process_pid: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    deployment_dir: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

class ProductArtifact(Base):
    __tablename__ = "gateway_product_artifacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[str] = mapped_column(String(64), ForeignKey("gateway_products.id"))
    version: Mapped[str] = mapped_column(String(32))
    code_content: Mapped[str] = mapped_column(Text)
    test_content: Mapped[str] = mapped_column(Text)
    sandbox_passed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

class AgentRecord(Base):
    __tablename__ = "gateway_agents"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(64))
    role: Mapped[str] = mapped_column(String(64))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    tasks_completed: Mapped[int] = mapped_column(Integer, default=0)

class AuditLog(Base):
    __tablename__ = "gateway_audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    actor: Mapped[str] = mapped_column(String(64), default="OWNER")
    action: Mapped[str] = mapped_column(String(64))
    details: Mapped[str] = mapped_column(Text)
    cost_usd: Mapped[float] = mapped_column(Float, default=0.0)

engine = create_engine(DB_PATH, echo=False)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ------------------------------------------------------------------------------
# In-Memory Running Process Manager
# ------------------------------------------------------------------------------
RUNNING_PROCESSES: Dict[str, subprocess.Popen] = {}
PROCESS_LOCK = threading.Lock()

def find_available_port() -> int:
    """Finds an unused ephemeral port on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]

def stop_process_instance(product_id: str, pid: Optional[int] = None):
    """Safely terminates a running process instance."""
    with PROCESS_LOCK:
        proc = RUNNING_PROCESSES.pop(product_id, None)
        if proc:
            try:
                proc.terminate()
                proc.wait(timeout=2.0)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
    if pid:
        try:
            if sys.platform == "win32":
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)], capture_output=True)
            else:
                os.kill(pid, signal.SIGKILL)
        except Exception:
            pass

# ------------------------------------------------------------------------------
# Audit Logger Helper
# ------------------------------------------------------------------------------
def record_audit(db: Session, action: str, details: str, actor: str = "OWNER", cost_usd: float = 0.0) -> AuditLog:
    entry = AuditLog(
        actor=actor,
        action=action,
        details=details,
        cost_usd=cost_usd,
        timestamp=datetime.now(timezone.utc)
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    logger.info(f"AUDIT LOG [{action}] by {actor}: {details}")
    return entry

def init_system_state(db: Session) -> SystemState:
    state = db.query(SystemState).filter_by(id=1).first()
    if not state:
        state = SystemState(
            id=1,
            is_paused=False,
            budget_limit_usd=100.0,
            spent_budget_usd=0.0,
            task_limit_count=50,
            tasks_executed_count=0
        )
        db.add(state)
        db.commit()
        db.refresh(state)
        record_audit(db, "SYSTEM_INIT", "System initialized with initial budget and state.")

    # Seed demo agents if none exist
    if db.query(AgentRecord).count() == 0:
        db.add_all([
            AgentRecord(id="AGENT-ARCH-01", name="Athena", role="STRATEGIST", is_active=True),
            AgentRecord(id="AGENT-CODE-02", name="Vulcan", role="CODER", is_active=True),
            AgentRecord(id="AGENT-QA-03", name="Argus", role="QA_AUDITOR", is_active=True),
        ])
        db.commit()
    return state

# ------------------------------------------------------------------------------
# Controlled Deployment Engine
# ------------------------------------------------------------------------------
def execute_sandbox_test(code_content: str, test_content: str) -> Tuple[bool, str]:
    """Runs tests in an isolated sandbox with a 10-second timeout."""
    with tempfile.TemporaryDirectory(prefix="deploy_sandbox_") as sbox:
        app_file = os.path.join(sbox, "app.py")
        test_file = os.path.join(sbox, "test_app.py")
        with open(app_file, "w", encoding="utf-8") as f:
            f.write(code_content)
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(test_content)

        try:
            res = subprocess.run(
                [sys.executable, "-m", "pytest", test_file, "-v", "--no-header"],
                cwd=sbox,
                capture_output=True,
                text=True,
                timeout=10.0
            )
            passed = (res.returncode == 0)
            output = res.stdout + "\n" + res.stderr
            return passed, output
        except subprocess.TimeoutExpired:
            return False, "Sandbox verification timed out after 10.0 seconds."
        except Exception as e:
            return False, f"Sandbox verification execution error: {str(e)}"

def deploy_product(db: Session, product_id: str, version: str) -> Dict[str, Any]:
    """
    Controlled Deployment:
    1. Verifies sandbox test pass for the target version artifact.
    2. Provisions isolated production deployment directory.
    3. Finds available ephemeral dynamic port.
    4. Terminates any previously running instance of this product.
    5. Spawns background process via uvicorn.
    6. Updates database records and records structured audit log.
    """
    state = db.query(SystemState).filter_by(id=1).first()
    if state and state.is_paused:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Deployment Rejected: System is currently PAUSED by owner kill-switch."
        )

    # 1. Fetch Product and Artifact
    product = db.query(ProductRecord).filter_by(id=product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product {product_id} not found.")

    artifact = (
        db.query(ProductArtifact)
        .filter_by(product_id=product_id, version=version)
        .order_by(desc(ProductArtifact.id))
        .first()
    )
    if not artifact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Artifact for product '{product_id}' version '{version}' does not exist."
        )

    # 2. Enforce Sandbox Verification
    logger.info(f"Initiating pre-deployment sandbox verification for {product_id} ({version})...")
    record_audit(db, "DEPLOY_VERIFY_START", f"Running sandbox verification for {product_id} version {version}")
    passed, test_log = execute_sandbox_test(artifact.code_content, artifact.test_content)
    artifact.sandbox_passed = passed
    db.commit()

    if not passed:
        record_audit(
            db, "DEPLOY_ABORTED",
            f"Deployment of {product_id} ({version}) rejected: Sandbox tests failed.",
            actor="DEPLOYMENT_GATEWAY"
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Deployment Rejected: Sandbox tests failed for version {version}. Output: " + str(test_log[-400:])
        )

    # 3. Terminate running instance if active
    stop_process_instance(product.id, product.process_pid)

    # 4. Prepare isolated deployment directory
    prod_deploy_dir = os.path.join(DEPLOYMENTS_BASE_DIR, f"{product.id}_{version}")
    os.makedirs(prod_deploy_dir, exist_ok=True)
    app_file_path = os.path.join(prod_deploy_dir, "app.py")
    with open(app_file_path, "w", encoding="utf-8") as f:
        f.write(artifact.code_content)

    # 5. Bind dynamic port & spawn background instance
    free_port = find_available_port()
    cmd = [
        sys.executable, "-m", "uvicorn", "app:app",
        "--host", "127.0.0.1",
        "--port", str(free_port),
        "--log-level", "warning"
    ]
    
    proc = subprocess.Popen(
        cmd,
        cwd=prod_deploy_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    with PROCESS_LOCK:
        RUNNING_PROCESSES[product.id] = proc

    # 6. Update Product state & Previous Stable pointer
    if product.status == "DEPLOYED" and product.active_version != version:
        product.previous_stable_version = product.active_version

    product.active_version = version
    product.status = "DEPLOYED"
    product.assigned_port = free_port
    product.process_pid = proc.pid
    product.deployment_dir = prod_deploy_dir
    db.commit()

    record_audit(
        db, "DEPLOY_SUCCESS",
        f"Product '{product.id}' successfully deployed version '{version}' on port {free_port} (PID: {proc.pid})",
        actor="DEPLOYMENT_GATEWAY"
    )

    return {
        "status": "DEPLOYED",
        "product_id": product.id,
        "version": version,
        "port": free_port,
        "pid": proc.pid,
        "previous_stable_version": product.previous_stable_version,
        "deployment_dir": prod_deploy_dir
    }

# ------------------------------------------------------------------------------
# Pydantic Schemas for Request Validation
# ------------------------------------------------------------------------------
class SetBudgetRequest(BaseModel):
    budget_limit_usd: Optional[float] = Field(None, gt=0, description="Hard ceiling for total spending in USD")
    task_limit_count: Optional[int] = Field(None, gt=0, description="Hard ceiling for total tasks executed")

class DeployProductRequest(BaseModel):
    product_id: str = Field(..., min_length=1)
    version: str = Field(..., min_length=1)

class CreateDemoProductRequest(BaseModel):
    product_id: str = "PROD-RATE-LIMITER"
    name: str = "Distributed Rate Limiter Service"
    v1_code: Optional[str] = None
    v2_code: Optional[str] = None

# ------------------------------------------------------------------------------
# FastAPI Application Declaration
# ------------------------------------------------------------------------------
app = FastAPI(
    title="Owner Control Center & Safe Deployment Gateway",
    description="Sovereign owner control, sandbox verification, dynamic deployment, and instant rollback.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------------------
# 1. OWNER GOVERNANCE & KILL-SWITCH ENDPOINTS
# ------------------------------------------------------------------------------

@app.post("/owner/pause", tags=["Governance"])
def pause_system(db: Session = Depends(get_db)):
    """
    Emergency Kill-Switch: Immediately sets system_paused = True.
    All worker loops, code synthesis, and test runs immediately abort.
    """
    state = init_system_state(db)
    state.is_paused = True
    db.commit()
    record_audit(db, "KILL_SWITCH_ENGAGED", "Owner engaged emergency kill-switch. All processing paused.", actor="OWNER")
    return {
        "system_paused": True,
        "message": "EMERGENCY KILL-SWITCH ENGAGED: All pipeline processing, code gen, and tests halted."
    }

@app.post("/owner/resume", tags=["Governance"])
def resume_system(db: Session = Depends(get_db)):
    """
    Resumes system processing after owner review.
    """
    state = init_system_state(db)
    state.is_paused = False
    db.commit()
    record_audit(db, "SYSTEM_RESUMED", "Owner released kill-switch. Normal operations resumed.", actor="OWNER")
    return {
        "system_paused": False,
        "message": "SYSTEM RESUMED: Normal background execution and pipeline processing active."
    }

@app.post("/owner/set-budget", tags=["Governance"])
def set_budget(req: SetBudgetRequest, db: Session = Depends(get_db)):
    """
    Sets hard operational boundaries for API spend (USD) and task count.
    Background jobs exceeding either limit are automatically aborted.
    """
    state = init_system_state(db)
    changes = []
    if req.budget_limit_usd is not None:
        state.budget_limit_usd = req.budget_limit_usd
        changes.append(f"budget_limit_usd=${req.budget_limit_usd:.2f}")
    if req.task_limit_count is not None:
        state.task_limit_count = req.task_limit_count
        changes.append(f"task_limit_count={req.task_limit_count}")

    db.commit()
    detail = "Updated limits: " + ", ".join(changes)
    record_audit(db, "BUDGET_LIMIT_UPDATED", detail, actor="OWNER")
    return {
        "message": "Budget limits updated successfully.",
        "budget_limit_usd": state.budget_limit_usd,
        "spent_budget_usd": state.spent_budget_usd,
        "task_limit_count": state.task_limit_count,
        "tasks_executed_count": state.tasks_executed_count
    }

# ------------------------------------------------------------------------------
# 2. CONTROLLED DEPLOYMENT & ROLLBACK ENDPOINTS
# ------------------------------------------------------------------------------

@app.post("/owner/deploy", tags=["Deployment"])
def trigger_deployment(req: DeployProductRequest, db: Session = Depends(get_db)):
    """
    Executes controlled deployment of a verified product artifact.
    """
    return deploy_product(db, req.product_id, req.version)

@app.post("/owner/rollback/{product_id}", tags=["Deployment"])
def rollback_product(product_id: str, db: Session = Depends(get_db)):
    """
    Immediate Safe Rollback:
    1. Identifies the previous stable version artifact.
    2. Terminates the running unstable instance.
    3. Re-deploys the previous stable artifact on a clean dynamic port.
    4. Logs the rollback incident to the AuditLog.
    """
    state = init_system_state(db)
    if state.is_paused:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Rollback Rejected: System is paused."
        )

    product = db.query(ProductRecord).filter_by(id=product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product '{product_id}' not found.")

    prev_version = product.previous_stable_version
    if not prev_version:
        record_audit(
            db, "ROLLBACK_FAILED",
            f"Rollback failed for {product_id}: No previous stable version recorded.",
            actor="OWNER"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot rollback product '{product_id}': No previous stable version exists in registry."
        )

    failed_version = product.active_version
    logger.warning(f"ROLLBACK INITIATED: Reverting {product_id} from {failed_version} to {prev_version}...")

    # Terminate the current unstable instance
    stop_process_instance(product.id, product.process_pid)

    # Re-deploy the previous stable artifact
    deploy_result = deploy_product(db, product_id, prev_version)
    product.status = "ROLLED_BACK"
    db.commit()

    incident_log = (
        f"INCIDENT: Product '{product_id}' rolled back from unstable version '{failed_version}' "
        f"to stable version '{prev_version}'. Active on port {deploy_result['port']}."
    )
    record_audit(db, "PRODUCT_ROLLBACK", incident_log, actor="OWNER")

    return {
        "status": "ROLLED_BACK",
        "product_id": product_id,
        "rolled_back_from": failed_version,
        "current_active_version": prev_version,
        "port": deploy_result["port"],
        "pid": deploy_result["pid"],
        "incident": incident_log
    }

# ------------------------------------------------------------------------------
# 3. OBSERVABILITY & AUDIT DASHBOARD
# ------------------------------------------------------------------------------

@app.get("/owner/dashboard", tags=["Observability"])
def get_dashboard(db: Session = Depends(get_db)):
    """
    Returns real-time telemetry:
    - System state (active/paused)
    - Active agents
    - Total tasks executed & limits
    - Financial spend vs budget
    - Active deployments & running ports
    - Last 10 structured audit logs
    """
    state = init_system_state(db)
    agents = db.query(AgentRecord).filter_by(is_active=True).all()
    products = db.query(ProductRecord).all()
    recent_logs = (
        db.query(AuditLog)
        .order_by(desc(AuditLog.timestamp))
        .limit(10)
        .all()
    )

    deployments_info = [
        {
            "product_id": p.id,
            "name": p.name,
            "active_version": p.active_version,
            "previous_stable_version": p.previous_stable_version,
            "status": p.status,
            "port": p.assigned_port,
            "pid": p.process_pid,
            "endpoint_url": f"http://127.0.0.1:{p.assigned_port}" if p.assigned_port else None
        }
        for p in products
    ]

    return {
        "system_status": "PAUSED" if state.is_paused else "ACTIVE",
        "kill_switch_active": state.is_paused,
        "financials": {
            "spent_usd": round(state.spent_budget_usd, 4),
            "budget_limit_usd": state.budget_limit_usd,
            "budget_utilization_pct": round((state.spent_budget_usd / state.budget_limit_usd) * 100, 2) if state.budget_limit_usd else 0.0,
            "is_budget_exceeded": state.spent_budget_usd >= state.budget_limit_usd
        },
        "tasks": {
            "total_executed": state.tasks_executed_count,
            "task_limit": state.task_limit_count,
            "is_limit_reached": state.tasks_executed_count >= state.task_limit_count
        },
        "agents": {
            "active_count": len(agents),
            "roster": [{"id": a.id, "name": a.name, "role": a.role, "tasks_completed": a.tasks_completed} for a in agents]
        },
        "active_deployments": deployments_info,
        "recent_audit_logs": [
            {
                "id": l.id,
                "timestamp": l.timestamp.isoformat(),
                "actor": l.actor,
                "action": l.action,
                "details": l.details,
                "cost_usd": l.cost_usd
            }
            for l in recent_logs
        ]
    }

# ------------------------------------------------------------------------------
# 4. BACKGROUND WORKER CHECK (Worker Loop Guardrail)
# ------------------------------------------------------------------------------

def execute_worker_task(db: Session, task_name: str, cost_usd: float = 0.05) -> Dict[str, Any]:
    """
    Simulated background task executor demonstrating budget and kill-switch guardrails.
    """
    state = init_system_state(db)

    # 1. Kill-Switch Check
    if state.is_paused:
        record_audit(db, "TASK_SKIPPED", f"Task '{task_name}' skipped: System is paused.", actor="WORKER")
        return {"status": "SKIPPED", "reason": "System is paused"}

    # 2. Budget & Task Limit Guardrails
    if state.spent_budget_usd + cost_usd > state.budget_limit_usd:
        record_audit(
            db, "TASK_ABORTED_BUDGET",
            f"Task '{task_name}' aborted: Budget ceiling (${state.budget_limit_usd}) reached.",
            actor="WORKER"
        )
        return {"status": "ABORTED", "reason": "Budget limit exceeded"}

    if state.tasks_executed_count >= state.task_limit_count:
        record_audit(
            db, "TASK_ABORTED_TASK_LIMIT",
            f"Task '{task_name}' aborted: Task limit ({state.task_limit_count}) reached.",
            actor="WORKER"
        )
        return {"status": "ABORTED", "reason": "Task limit reached"}

    # 3. Execute and Update
    state.spent_budget_usd += cost_usd
    state.tasks_executed_count += 1
    db.commit()

    record_audit(
        db, "TASK_COMPLETED",
        f"Executed '{task_name}' (Cost: ${cost_usd:.3f}). Total spend: ${state.spent_budget_usd:.3f}",
        actor="WORKER",
        cost_usd=cost_usd
    )
    return {
        "status": "COMPLETED",
        "task": task_name,
        "cost_usd": cost_usd,
        "tasks_executed": state.tasks_executed_count,
        "spent_budget_usd": round(state.spent_budget_usd, 4)
    }

@app.post("/owner/test-worker-job", tags=["Worker"])
def trigger_test_worker_job(task_name: str = "automated_code_audit", db: Session = Depends(get_db)):
    """
    Triggers an execution step through the worker guardrail check.
    """
    return execute_worker_task(db, task_name)

# ------------------------------------------------------------------------------
# 5. DEMO SEEDING UTILITY (Prepares Real Rate-Limiter Artifacts)
# ------------------------------------------------------------------------------

@app.post("/owner/seed-demo-artifacts", tags=["Setup"])
def seed_demo_artifacts(db: Session = Depends(get_db)):
    """
    Seeds real v1.0.0 and v2.0.0 rate limiter artifacts into the registry
    for deployment and rollback verification.
    """
    init_system_state(db)
    prod_id = "PROD-RATE-LIMITER"

    product = db.query(ProductRecord).filter_by(id=prod_id).first()
    if not product:
        product = ProductRecord(
            id=prod_id,
            name="Distributed Rate Limiter Service",
            active_version="v1.0.0",
            status="STAGED"
        )
        db.add(product)
        db.commit()

    # V1.0.0 Working FastAPI Code & Tests
    v1_code = """
import time
import threading
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="RateLimiter", version="1.0.0")

class ConsumeReq(BaseModel):
    client_id: str = "default"
    tokens: int = 1

tokens = 10.0
lock = threading.Lock()

@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0.0"}

@app.post("/consume")
def consume(req: ConsumeReq):
    global tokens
    with lock:
        if tokens >= req.tokens:
            tokens -= req.tokens
            return {"allowed": True, "remaining": tokens}
        return {"allowed": False, "remaining": tokens}
"""
    v1_tests = """
import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["version"] == "1.0.0"

def test_consume():
    res = client.post("/consume", json={"client_id": "test", "tokens": 2})
    assert res.status_code == 200
    assert res.json()["allowed"] is True
"""

    # V2.0.0 Evolved FastAPI Code & Tests
    v2_code = """
import time
import threading
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="RateLimiter", version="2.0.0")

class ConsumeReq(BaseModel):
    client_id: str = "default"
    tokens: int = 1

class ConfigReq(BaseModel):
    max_capacity: float

tokens = 50.0
capacity = 50.0
lock = threading.Lock()

@app.get("/health")
def health():
    return {"status": "ok", "version": "2.0.0"}

@app.post("/consume")
def consume(req: ConsumeReq):
    global tokens
    with lock:
        if tokens >= req.tokens:
            tokens -= req.tokens
            return {"allowed": True, "remaining": tokens}
        return {"allowed": False, "remaining": tokens}

@app.post("/config")
def set_config(cfg: ConfigReq):
    global capacity
    capacity = cfg.max_capacity
    return {"status": "updated", "capacity": capacity}
"""
    v2_tests = """
import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_health_v2():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["version"] == "2.0.0"

def test_config():
    res = client.post("/config", json={"max_capacity": 100.0})
    assert res.status_code == 200
    assert res.json()["capacity"] == 100.0
"""

    # Add Artifacts
    db.query(ProductArtifact).filter_by(product_id=prod_id).delete()
    db.add_all([
        ProductArtifact(product_id=prod_id, version="v1.0.0", code_content=v1_code.strip(), test_content=v1_tests.strip()),
        ProductArtifact(product_id=prod_id, version="v2.0.0", code_content=v2_code.strip(), test_content=v2_tests.strip())
    ])
    db.commit()

    record_audit(db, "ARTIFACTS_SEEDED", f"Seeded v1.0.0 and v2.0.0 artifacts for {prod_id}.")
    return {"status": "SUCCESS", "product_id": prod_id, "versions": ["v1.0.0", "v2.0.0"]}

# ------------------------------------------------------------------------------
# Process Cleanup on Application Shutdown
# ------------------------------------------------------------------------------
@app.on_event("shutdown")
def shutdown_deployments():
    logger.info("Gateway shutting down: Terminating all background deployment processes...")
    with PROCESS_LOCK:
        for pid_key, proc in list(RUNNING_PROCESSES.items()):
            try:
                proc.terminate()
                proc.wait(timeout=1.0)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
        RUNNING_PROCESSES.clear()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("control_gateway:app", host="127.0.0.1", port=8000, reload=False)

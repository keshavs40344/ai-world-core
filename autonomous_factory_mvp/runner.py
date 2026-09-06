"""
Deterministic 24x7 Scheduler & Worker Loop
Features:
- Periodic Tick Advancement without unnecessary LLM calls
- Owner Pause Switch Guardrail
- Strict Spend / Budget Enforcement
"""

import time
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from .models import World, Company, Agent, Task, Product, AuditLog, generate_id
from .engine import PipelineEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("AutonomousFactoryRunner")

class FactoryRunner:
    def __init__(self, session: Session, world_id: str):
        self.session = session
        self.world_id = world_id
        self.pipeline = PipelineEngine(session)

    def get_world(self) -> World:
        world = self.session.query(World).filter_by(id=self.world_id).first()
        if not world:
            raise ValueError(f"World {self.world_id} does not exist.")
        return world

    def toggle_owner_pause(self, is_paused: bool) -> bool:
        """Owner Switch: Hard-pauses or resumes all world operations."""
        world = self.get_world()
        world.is_paused = is_paused
        audit = AuditLog(
            id=generate_id("LOG"),
            world_id=world.id,
            actor_agent_id="OWNER",
            action="WORLD_PAUSE_TOGGLE",
            details=f"Owner set is_paused={is_paused}",
            cost_usd=0.0
        )
        self.session.add(audit)
        self.session.commit()
        logger.warning(f"OWNER ACTION: World pause status set to {is_paused}")
        return world.is_paused

    def record_spending(self, cost_usd: float) -> bool:
        """Safety & Cost Guardrail: Enforces hard spending ceiling."""
        world = self.get_world()
        if world.spent_budget_usd + cost_usd > world.budget_limit_usd:
            logger.error(
                f"SAFETY GUARDRAIL TRIGGERED: Spending ceiling reached! "
                f"Attempted: ${world.spent_budget_usd + cost_usd:.2f} / Limit: ${world.budget_limit_usd:.2f}"
            )
            world.is_paused = True
            self.session.commit()
            return False
        world.spent_budget_usd += cost_usd
        self.session.commit()
        return True

    def process_next_task(self) -> Optional[Dict[str, Any]]:
        """Processes the next task from the deterministic queue."""
        world = self.get_world()
        if world.is_paused:
            logger.info("Scheduler Tick Skipped: World is PAUSED by Owner.")
            return {"status": "PAUSED", "reason": "Owner pause switch active"}

        # Advance tick counter
        world.clock_tick += 1
        self.session.commit()

        # Query pending task
        task = (
            self.session.query(Task)
            .filter_by(status="QUEUED")
            .order_by(Task.created_at.asc())
            .first()
        )

        if not task:
            return {"status": "IDLE", "tick": world.clock_tick, "message": "Zero pending tasks in queue."}

        # Check budget limit before processing
        task_cost = 0.015
        if not self.record_spending(task_cost):
            task.status = "FAILED"
            task.result_json = '{"error": "Budget limit exceeded"}'
            self.session.commit()
            return {"status": "BUDGET_EXCEEDED", "task_id": task.id}

        # Process Task Deterministically
        logger.info(f"Processing Task: {task.id} (Type: {task.task_type}) on Tick #{world.clock_tick}")
        task.status = "IN_PROGRESS"
        self.session.commit()

        # Execute according to task type
        company = self.session.query(Company).filter_by(id=task.company_id).first()
        agents = {a.role: a.id for a in company.agents}

        if task.task_type == "RUN_CLOSED_LOOP":
            # Execute the full 4-step lifecycle
            spec = self.pipeline.step_1_identify_problem(company.id, agents.get("STRATEGIST", "AGENT-01"))
            code, tests = self.pipeline.step_2_synthesize_v1_code(company.id, agents.get("CODER", "AGENT-02"), spec)
            prod = self.pipeline.step_3_qa_and_deploy_v1(company.id, agents.get("QA_AUDITOR", "AGENT-03"), spec, code, tests)
            prod_v2 = self.pipeline.step_4_feedback_and_patch_v2(company.id, agents.get("CODER", "AGENT-02"), agents.get("QA_AUDITOR", "AGENT-03"), prod)

            task.status = "COMPLETED"
            task.result_json = f'{{"product_id": "{prod_v2.id}", "final_version": "{prod_v2.version}", "status": "{prod_v2.status}"}}'
            task.completed_at = datetime.now(timezone.utc)
            self.session.commit()
            return {"status": "SUCCESS", "task_id": task.id, "product": prod_v2.name, "version": prod_v2.version}

        task.status = "COMPLETED"
        task.completed_at = datetime.now(timezone.utc)
        self.session.commit()
        return {"status": "COMPLETED", "task_id": task.id}

    def run_continuous_loop(self, max_ticks: int = 5, sleep_sec: float = 1.0):
        """Runs the deterministic loop for N ticks (or indefinitely if max_ticks=0)."""
        logger.info(f"Starting Deterministic Factory Runner Loop (Max Ticks: {max_ticks})")
        ticks_run = 0
        while max_ticks == 0 or ticks_run < max_ticks:
            res = self.process_next_task()
            logger.info(f"Cycle Result: {res}")
            ticks_run += 1
            time.sleep(sleep_sec)
        logger.info("Factory Runner Loop finished requested cycles.")

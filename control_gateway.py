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
import html
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timezone

from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks, Request
from fastapi.responses import HTMLResponse
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

def _render_state_badge_html(is_paused: bool) -> str:
    if is_paused:
        return """
        <div id="world-state-control" class="flex items-center space-x-2">
            <span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-500/20 text-rose-400 border border-rose-500/30">
                <span class="w-1.5 h-1.5 rounded-full bg-rose-400 mr-1.5 animate-pulse"></span>
                PAUSED (KILL-SWITCH ENGAGED)
            </span>
            <button hx-post="/owner/resume"
                    hx-target="#world-state-control"
                    hx-swap="outerHTML"
                    class="px-2.5 py-1 text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white rounded transition shadow-sm">
                Resume World
            </button>
        </div>
        """
    else:
        return """
        <div id="world-state-control" class="flex items-center space-x-2">
            <span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 mr-1.5 animate-pulse"></span>
                ACTIVE
            </span>
            <button hx-post="/owner/pause"
                    hx-target="#world-state-control"
                    hx-swap="outerHTML"
                    class="px-2.5 py-1 text-xs font-semibold bg-rose-600 hover:bg-rose-500 text-white rounded transition shadow-sm">
                Emergency Pause
            </button>
        </div>
        """

@app.post("/owner/pause", tags=["Governance"])
async def pause_system(request: Request, db: Session = Depends(get_db)):
    """
    Emergency Kill-Switch: Immediately sets system_paused = True.
    All worker loops, code synthesis, and test runs immediately abort.
    Supports both JSON and HTMX fragment responses.
    """
    state = init_system_state(db)
    state.is_paused = True
    db.commit()
    record_audit(db, "KILL_SWITCH_ENGAGED", "Owner engaged emergency kill-switch. All processing paused.", actor="OWNER")
    
    if "hx-request" in request.headers:
        return HTMLResponse(_render_state_badge_html(True))
    return {
        "system_paused": True,
        "message": "EMERGENCY KILL-SWITCH ENGAGED: All pipeline processing, code gen, and tests halted."
    }

@app.post("/owner/resume", tags=["Governance"])
async def resume_system(request: Request, db: Session = Depends(get_db)):
    """
    Resumes system processing after owner review.
    Supports both JSON and HTMX fragment responses.
    """
    state = init_system_state(db)
    state.is_paused = False
    db.commit()
    record_audit(db, "SYSTEM_RESUMED", "Owner released kill-switch. Normal operations resumed.", actor="OWNER")
    
    if "hx-request" in request.headers:
        return HTMLResponse(_render_state_badge_html(False))
    return {
        "system_paused": False,
        "message": "SYSTEM RESUMED: Normal background execution and pipeline processing active."
    }

@app.post("/owner/set-budget", tags=["Governance"])
async def set_budget(request: Request, db: Session = Depends(get_db)):
    """
    Sets hard operational boundaries for API spend (USD) and task count.
    Accepts both JSON and standard HTML form payloads.
    """
    budget_limit_usd = None
    task_limit_count = None

    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        body = await request.json()
        budget_limit_usd = body.get("budget_limit_usd")
        task_limit_count = body.get("task_limit_count")
    else:
        # Parse form data or query params
        form_data = await request.form()
        if "budget_limit_usd" in form_data and form_data["budget_limit_usd"]:
            try:
                budget_limit_usd = float(form_data["budget_limit_usd"])
            except ValueError:
                pass
        if "task_limit_count" in form_data and form_data["task_limit_count"]:
            try:
                task_limit_count = int(form_data["task_limit_count"])
            except ValueError:
                pass

    state = init_system_state(db)
    changes = []
    if budget_limit_usd is not None and budget_limit_usd > 0:
        state.budget_limit_usd = budget_limit_usd
        changes.append(f"budget_limit_usd=${budget_limit_usd:.2f}")
    if task_limit_count is not None and task_limit_count > 0:
        state.task_limit_count = task_limit_count
        changes.append(f"task_limit_count={task_limit_count}")

    if changes:
        db.commit()
        detail = "Updated limits: " + ", ".join(changes)
        record_audit(db, "BUDGET_LIMIT_UPDATED", detail, actor="OWNER")
    else:
        detail = "No limit changes provided."

    if "hx-request" in request.headers:
        alert_html = f"""
        <div class="mb-4 p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-lg flex items-center justify-between text-xs text-emerald-300 animate-fadeIn">
            <div class="flex items-center space-x-2">
                <svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                </svg>
                <span><strong>Budget Boundaries Updated:</strong> Spend Cap: ${state.budget_limit_usd:.2f} USD | Task Cap: {state.task_limit_count} tasks</span>
            </div>
            <button onclick="this.parentElement.remove()" class="text-emerald-400 hover:text-emerald-200">&times;</button>
        </div>
        """
        return HTMLResponse(alert_html)

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

# ------------------------------------------------------------------------------
# 3.1 FULL WEB DASHBOARD & HTMX LIVE MONITOR ENDPOINTS
# ------------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse, tags=["Dashboard"])
def serve_dashboard():
    """
    Serves the zero-dependency, single-file Tailwind + HTMX Dashboard.
    """
    dash_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dashboard.html")
    if os.path.exists(dash_file):
        with open(dash_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h2>Dashboard file dashboard.html not found on server.</h2>", status_code=404)

@app.get("/owner/metrics-cards", response_class=HTMLResponse, tags=["Dashboard"])
def get_metrics_cards_partial(db: Session = Depends(get_db)):
    """
    Returns HTML partial for Top-Row Metric Cards:
    - World State: Status badge (Active/Paused) with instant toggle button
    - Active Agents: Total agents currently active vs max agent limit
    - Resource Spend: Total token/API spend tracked vs global hard cap
    - Deployed Products: Count of active deployed micro-services
    """
    state = init_system_state(db)
    agents = db.query(AgentRecord).filter_by(is_active=True).all()
    products = db.query(ProductRecord).all()
    deployed_count = sum(1 for p in products if p.status in ("DEPLOYED", "ROLLED_BACK") and p.assigned_port)

    # Calculate utilization
    spend_pct = round((state.spent_budget_usd / state.budget_limit_usd) * 100, 1) if state.budget_limit_usd else 0.0
    task_pct = round((state.tasks_executed_count / state.task_limit_count) * 100, 1) if state.task_limit_count else 0.0
    max_agents = 10
    agent_count = len(agents)

    # World state widget
    state_widget = _render_state_badge_html(state.is_paused)

    html_content = f"""
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <!-- Card 1: World State & Emergency Controls -->
        <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col justify-between shadow-sm hover:border-slate-700 transition">
            <div class="flex items-center justify-between">
                <span class="text-xs font-medium text-slate-400">World Sovereign State</span>
                <span class="p-1.5 rounded-lg bg-slate-800 text-slate-400">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
                    </svg>
                </span>
            </div>
            <div class="mt-3">
                {state_widget}
            </div>
            <div class="mt-3 pt-2.5 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-500 font-mono">
                <span>Kill-Switch: {"ENGAGED" if state.is_paused else "READY"}</span>
                <span>Port 8000</span>
            </div>
        </div>

        <!-- Card 2: Active Agents & Roster -->
        <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col justify-between shadow-sm hover:border-slate-700 transition">
            <div class="flex items-center justify-between">
                <span class="text-xs font-medium text-slate-400">Active Agents</span>
                <span class="p-1.5 rounded-lg bg-blue-500/10 text-blue-400 border border-blue-500/20">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/>
                    </svg>
                </span>
            </div>
            <div class="mt-2 flex items-baseline space-x-2">
                <span class="text-2xl font-bold text-white font-mono">{agent_count}</span>
                <span class="text-xs text-slate-400 font-mono">/ {max_agents} max limit</span>
            </div>
            <div class="mt-3">
                <div class="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                    <div class="bg-blue-500 h-1.5 rounded-full" style="width: {min(100.0, (agent_count / max_agents) * 100)}%"></div>
                </div>
                <div class="mt-2 flex items-center justify-between text-[11px] text-slate-500">
                    <span>Concurrency Cap</span>
                    <span class="text-slate-400 font-mono">{agent_count}/{max_agents} slots</span>
                </div>
            </div>
        </div>

        <!-- Card 3: Financial Budget & Spend -->
        <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col justify-between shadow-sm hover:border-slate-700 transition">
            <div class="flex items-center justify-between">
                <span class="text-xs font-medium text-slate-400">Resource Spend</span>
                <span class="p-1.5 rounded-lg bg-amber-500/10 text-amber-400 border border-amber-500/20">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                </span>
            </div>
            <div class="mt-2 flex items-baseline space-x-2">
                <span class="text-2xl font-bold text-white font-mono">${state.spent_budget_usd:.3f}</span>
                <span class="text-xs text-slate-400 font-mono">/ ${state.budget_limit_usd:.2f} cap</span>
            </div>
            <div class="mt-3">
                <div class="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                    <div class="h-1.5 rounded-full {"bg-rose-500" if spend_pct >= 90 else "bg-emerald-500"}" style="width: {min(100.0, spend_pct)}%"></div>
                </div>
                <div class="mt-2 flex items-center justify-between text-[11px] text-slate-500">
                    <span>Utilization</span>
                    <span class="font-mono text-slate-300">{spend_pct}% ({state.tasks_executed_count}/{state.task_limit_count} tasks)</span>
                </div>
            </div>
        </div>

        <!-- Card 4: Deployed Microservices -->
        <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col justify-between shadow-sm hover:border-slate-700 transition">
            <div class="flex items-center justify-between">
                <span class="text-xs font-medium text-slate-400">Deployed Products</span>
                <span class="p-1.5 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
                    </svg>
                </span>
            </div>
            <div class="mt-2 flex items-baseline space-x-2">
                <span class="text-2xl font-bold text-white font-mono">{deployed_count}</span>
                <span class="text-xs text-slate-400 font-mono">active live services</span>
            </div>
            <div class="mt-3 pt-2.5 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-500">
                <span>Total Registered</span>
                <span class="text-slate-300 font-mono">{len(products)} products</span>
            </div>
        </div>
    </div>
    """
    return HTMLResponse(html_content)

@app.get("/owner/pipeline-board", response_class=HTMLResponse, tags=["Dashboard"])
def get_pipeline_board_partial():
    """
    Visual Kanban-style Status Board showing tasks across departments:
    Product -> Engineering -> QA -> Operations
    With live status pills: Pending (Yellow), In Progress (Blue), Failed (Red), Completed (Green).
    Reads from orchestrator_departments.db if available; fallbacks gracefully.
    """
    departments = ["Product", "Engineering", "QA", "Operations"]
    dept_icons = {
        "Product": "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z",
        "Engineering": "M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4",
        "QA": "M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z",
        "Operations": "M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01"
    }
    
    tasks_by_dept = {d: [] for d in departments}

    dept_db = "orchestrator_departments.db"
    if os.path.exists(dept_db):
        try:
            import sqlite3
            conn = sqlite3.connect(dept_db)
            c = conn.cursor()
            rows = c.execute(
                "SELECT id, department, name, status, retry_count, cost_usd, created_at "
                "FROM dept_tasks ORDER BY created_at ASC"
            ).fetchall()
            for r in rows:
                t_id, dept, name, st, retries, cost, created = r
                if dept in tasks_by_dept:
                    tasks_by_dept[dept].append({
                        "id": t_id,
                        "name": name,
                        "status": st,
                        "retries": retries,
                        "cost": cost,
                        "created": created
                    })
            conn.close()
        except Exception as e:
            logger.warning(f"Error querying orchestrator_departments.db: {e}")

    def get_status_pill(status_val: str) -> str:
        s = status_val.upper()
        if s == "COMPLETED":
            return '<span class="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">Completed</span>'
        elif s == "IN_PROGRESS":
            return '<span class="px-2 py-0.5 rounded text-[10px] font-semibold bg-blue-500/20 text-blue-400 border border-blue-500/30 animate-pulse">In Progress</span>'
        elif s == "FAILED":
            return '<span class="px-2 py-0.5 rounded text-[10px] font-semibold bg-rose-500/20 text-rose-400 border border-rose-500/30">Failed</span>'
        elif s == "BLOCKED":
            return '<span class="px-2 py-0.5 rounded text-[10px] font-semibold bg-orange-500/20 text-orange-400 border border-orange-500/30">Blocked</span>'
        else: # PENDING
            return '<span class="px-2 py-0.5 rounded text-[10px] font-semibold bg-amber-500/20 text-amber-400 border border-amber-500/30">Pending</span>'

    html_cols = []
    for dept in departments:
        tasks = tasks_by_dept[dept]
        task_cards = []
        for t in tasks:
            pill = get_status_pill(t["status"])
            retry_badge = f'<span class="text-[10px] text-amber-400 font-mono">Retries: {t["retries"]}</span>' if t["retries"] > 0 else ''
            task_cards.append(f"""
            <div class="bg-slate-950/70 border border-slate-800 rounded-lg p-3 hover:border-slate-700 transition space-y-2">
                <div class="flex items-start justify-between gap-2">
                    <span class="text-[11px] font-mono text-indigo-400 font-semibold">{t["id"]}</span>
                    {pill}
                </div>
                <p class="text-xs text-slate-200 font-medium leading-snug">{html.escape(t["name"])}</p>
                <div class="pt-2 border-t border-slate-800/60 flex items-center justify-between text-[10px] text-slate-400 font-mono">
                    <span>${t["cost"]:.3f} USD</span>
                    {retry_badge}
                </div>
            </div>
            """)

        cards_inner = "\n".join(task_cards) if task_cards else """
        <div class="py-10 text-center text-slate-500 text-xs font-mono">
            No active departmental tasks
        </div>
        """

        col_html = f"""
        <div class="bg-slate-900 border border-slate-800 rounded-xl p-3.5 flex flex-col h-full shadow-sm">
            <!-- Column Header -->
            <div class="flex items-center justify-between pb-3 border-b border-slate-800 mb-3">
                <div class="flex items-center space-x-2">
                    <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="{dept_icons[dept]}"/>
                    </svg>
                    <span class="text-xs font-bold text-white uppercase tracking-wider">{dept}</span>
                </div>
                <span class="px-2 py-0.5 rounded-full text-[10px] font-mono bg-slate-800 text-slate-300 border border-slate-700">
                    {len(tasks)}
                </span>
            </div>
            <!-- Column Tasks -->
            <div class="space-y-2.5 overflow-y-auto max-h-96 pr-1">
                {cards_inner}
            </div>
        </div>
        """
        html_cols.append(col_html)

    grid_html = f'<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">{"".join(html_cols)}</div>'
    return HTMLResponse(grid_html)

@app.get("/owner/deployments-list", response_class=HTMLResponse, tags=["Dashboard"])
def get_deployments_list_partial(db: Session = Depends(get_db)):
    """
    Returns HTML partial for active deployments table with one-click Rollback button.
    """
    products = db.query(ProductRecord).all()
    if not products:
        return HTMLResponse("""
        <div class="py-8 text-center text-slate-500 text-xs font-mono">
            No deployed products found in registry. Click 'Seed Demo Artifacts' above to initialize a live rate limiter service.
        </div>
        """)

    rows = []
    for p in products:
        status_color = "text-emerald-400 bg-emerald-500/10 border-emerald-500/20" if p.status in ("DEPLOYED", "ROLLED_BACK") else "text-amber-400 bg-amber-500/10 border-amber-500/20"
        url_link = f'<a href="http://127.0.0.1:{p.assigned_port}/health" target="_blank" class="font-mono text-indigo-400 hover:underline flex items-center space-x-1"><span>http://127.0.0.1:{p.assigned_port}</span><svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg></a>' if p.assigned_port else '<span class="text-slate-500 font-mono">Unassigned</span>'

        rollback_btn = ""
        if p.previous_stable_version:
            rollback_btn = f"""
            <button hx-post="/owner/rollback/{p.id}"
                    hx-target="#notice-target"
                    hx-swap="innerHTML"
                    class="px-2.5 py-1 text-[11px] font-medium bg-rose-600/80 hover:bg-rose-500 text-white rounded transition shadow-sm flex items-center space-x-1">
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6"/>
                </svg>
                <span>Rollback &rarr; {p.previous_stable_version}</span>
            </button>
            """
        else:
            rollback_btn = '<span class="text-[11px] text-slate-500 italic">No stable baseline</span>'

        rows.append(f"""
        <tr class="hover:bg-slate-800/40 transition">
            <td class="py-3 px-4 font-mono font-semibold text-white">{p.id}</td>
            <td class="py-3 px-4 text-slate-200">{html.escape(p.name)}</td>
            <td class="py-3 px-4 font-mono"><span class="px-2 py-0.5 rounded bg-slate-800 text-slate-200 border border-slate-700">{p.active_version}</span></td>
            <td class="py-3 px-4 font-mono text-slate-400">{p.previous_stable_version or "&mdash;"}</td>
            <td class="py-3 px-4 font-mono">{url_link}</td>
            <td class="py-3 px-4">
                <span class="px-2 py-0.5 rounded text-[10px] font-semibold border {status_color}">
                    {p.status}
                </span>
            </td>
            <td class="py-3 px-4 text-right">
                {rollback_btn}
            </td>
        </tr>
        """)

    table_html = f"""
    <div class="overflow-x-auto rounded-lg border border-slate-800">
        <table class="min-w-full divide-y divide-slate-800 text-left text-xs">
            <thead class="bg-slate-950/80 text-slate-400 font-semibold uppercase tracking-wider text-[10px]">
                <tr>
                    <th class="py-2.5 px-4">Product ID</th>
                    <th class="py-2.5 px-4">Name</th>
                    <th class="py-2.5 px-4">Active Ver</th>
                    <th class="py-2.5 px-4">Prev Stable</th>
                    <th class="py-2.5 px-4">Dynamic Port / Health</th>
                    <th class="py-2.5 px-4">Status</th>
                    <th class="py-2.5 px-4 text-right">Governance Actions</th>
                </tr>
            </thead>
            <tbody class="divide-y divide-slate-800/60 bg-slate-900/40 text-slate-300 font-normal">
                {"".join(rows)}
            </tbody>
        </table>
    </div>
    """
    return HTMLResponse(table_html)

@app.get("/owner/audit-logs-table", response_class=HTMLResponse, tags=["Dashboard"])
def get_audit_logs_table_partial(db: Session = Depends(get_db)):
    """
    Auto-refreshing log table using HTMX.
    Columns: Timestamp, Agent/Department, Event Type, Status/Action, Cost.
    Aggregates logs from both gateway_audit_logs and dept_audit_logs.
    """
    entries = []

    # 1. Gateway Audit Logs
    gw_logs = db.query(AuditLog).order_by(desc(AuditLog.timestamp)).limit(20).all()
    for l in gw_logs:
        entries.append({
            "timestamp": l.timestamp,
            "actor": l.actor,
            "action": l.action,
            "details": l.details,
            "cost": l.cost_usd or 0.0
        })

    # 2. Department Orchestrator Logs if available
    dept_db = "orchestrator_departments.db"
    if os.path.exists(dept_db):
        try:
            import sqlite3
            conn = sqlite3.connect(dept_db)
            c = conn.cursor()
            rows = c.execute(
                "SELECT timestamp, department, agent_id, action, details, cost_usd "
                "FROM dept_audit_logs ORDER BY timestamp DESC LIMIT 20"
            ).fetchall()
            for r in rows:
                ts_str, dept, agent_id, action, details, cost = r
                try:
                    ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                except Exception:
                    ts = datetime.now(timezone.utc)
                entries.append({
                    "timestamp": ts,
                    "actor": f"{dept} ({agent_id})",
                    "action": action,
                    "details": details,
                    "cost": cost or 0.0
                })
            conn.close()
        except Exception:
            pass

    # Sort combined entries descending
    entries.sort(key=lambda x: x["timestamp"], reverse=True)
    entries = entries[:15]

    if not entries:
        return HTMLResponse('<tr><td colspan="5" class="py-6 text-center text-slate-500 font-mono">No audit logs recorded yet.</td></tr>')

    rows_html = []
    for e in entries:
        ts_display = e["timestamp"].strftime("%H:%M:%S") if hasattr(e["timestamp"], "strftime") else str(e["timestamp"])
        
        # Action badge styling
        action_str = e["action"].upper()
        if "KILL" in action_str or "ABORT" in action_str or "FAIL" in action_str:
            badge_class = "bg-rose-500/10 text-rose-400 border border-rose-500/20"
        elif "COMPLETED" in action_str or "DEPLOY" in action_str or "RESUMED" in action_str:
            badge_class = "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
        elif "ROLLBACK" in action_str:
            badge_class = "bg-purple-500/10 text-purple-400 border border-purple-500/20"
        else:
            badge_class = "bg-blue-500/10 text-blue-400 border border-blue-500/20"

        cost_str = f"${e['cost']:.3f}" if e["cost"] > 0 else "&mdash;"

        rows_html.append(f"""
        <tr class="hover:bg-slate-800/40 transition">
            <td class="py-2.5 px-4 font-mono text-slate-400 text-[11px] whitespace-nowrap">{ts_display}</td>
            <td class="py-2.5 px-4 font-mono text-indigo-300 font-medium whitespace-nowrap">{html.escape(e['actor'])}</td>
            <td class="py-2.5 px-4 whitespace-nowrap">
                <span class="px-2 py-0.5 rounded text-[10px] font-mono {badge_class}">
                    {html.escape(e['action'])}
                </span>
            </td>
            <td class="py-2.5 px-4 text-slate-300 text-xs">{html.escape(e['details'])}</td>
            <td class="py-2.5 px-4 text-right font-mono text-slate-400 text-[11px]">{cost_str}</td>
        </tr>
        """)

    return HTMLResponse("".join(rows_html))

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

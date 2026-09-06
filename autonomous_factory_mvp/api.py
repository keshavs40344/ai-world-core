"""
Lightweight FastAPI REST API for Autonomous Factory Control
Endpoints for state inspection, owner overrides, and manual closed-loop triggers.
"""

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from .models import World, Company, Agent, Task, Product, AuditLog, get_engine_and_session
from .runner import FactoryRunner

app = FastAPI(
    title="Autonomous Agentic Factory Core API",
    description="Clean, deterministic MVP of an autonomous software company.",
    version="1.0.0"
)

# Engine & Session Setup
engine, SessionLocal = get_engine_and_session("sqlite:///autonomous_factory_mvp/factory_core.db")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def ensure_seeded_world(db: Session) -> World:
    world = db.query(World).first()
    if not world:
        world = World(name="Genesis Sovereign World", budget_limit_usd=100.0)
        db.add(world)
        db.commit()

        comp = Company(world_id=world.id, name="Apex Micro-Software Lab", ticker="AMSL")
        db.add(comp)
        db.commit()

        # Founding Agents
        db.add(Agent(company_id=comp.id, name="Atlas", role="STRATEGIST"))
        db.add(Agent(company_id=comp.id, name="DaVinci", role="CODER"))
        db.add(Agent(company_id=comp.id, name="Sentinel", role="QA_AUDITOR"))
        db.commit()
    return world

@app.get("/health")
def health():
    return {"status": "ONLINE", "engine": "FastAPI + SQLAlchemy 2.0"}

@app.get("/world/status")
def get_world_status(db: Session = Depends(get_db)):
    world = ensure_seeded_world(db)
    companies = db.query(Company).filter_by(world_id=world.id).all()
    products = db.query(Product).all()
    tasks = db.query(Task).all()

    return {
        "world_id": world.id,
        "name": world.name,
        "is_paused": world.is_paused,
        "clock_tick": world.clock_tick,
        "spent_budget_usd": world.spent_budget_usd,
        "budget_limit_usd": world.budget_limit_usd,
        "total_companies": len(companies),
        "total_products": len(products),
        "total_tasks": len(tasks)
    }

@app.post("/world/pause")
def pause_world(db: Session = Depends(get_db)):
    world = ensure_seeded_world(db)
    runner = FactoryRunner(db, world.id)
    runner.toggle_owner_pause(True)
    return {"status": "SUCCESS", "is_paused": True, "message": "World operations paused."}

@app.post("/world/resume")
def resume_world(db: Session = Depends(get_db)):
    world = ensure_seeded_world(db)
    runner = FactoryRunner(db, world.id)
    runner.toggle_owner_pause(False)
    return {"status": "SUCCESS", "is_paused": False, "message": "World operations resumed."}

@app.get("/products")
def list_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "slug": p.slug,
            "version": p.version,
            "status": p.status,
            "test_exit_code": p.test_exit_code,
            "created_at": p.created_at.isoformat(),
            "updated_at": p.updated_at.isoformat()
        }
        for p in products
    ]

@app.post("/pipeline/trigger-closed-loop")
def trigger_closed_loop(db: Session = Depends(get_db)):
    world = ensure_seeded_world(db)
    comp = db.query(Company).filter_by(world_id=world.id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Company not found.")

    # Queue the closed loop task
    from .models import generate_id
    task = Task(
        id=generate_id("TASK"),
        company_id=comp.id,
        task_type="RUN_CLOSED_LOOP",
        status="QUEUED"
    )
    db.add(task)
    db.commit()

    # Process task with runner
    runner = FactoryRunner(db, world.id)
    res = runner.process_next_task()
    return {"task_result": res}

@app.get("/audit-logs")
def get_audit_logs(limit: int = 15, db: Session = Depends(get_db)):
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit).all()
    return [
        {
            "id": l.id,
            "actor": l.actor_agent_id,
            "action": l.action,
            "details": l.details,
            "cost_usd": l.cost_usd,
            "timestamp": l.timestamp.isoformat()
        }
        for l in logs
    ]

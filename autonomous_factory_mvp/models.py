"""
Core Data Models (SQLAlchemy 2.0 ORM)
Entities: World, Company, Agent, Task, Product, AuditLog
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, Float, Integer, Boolean, Text, DateTime, ForeignKey, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

class Base(DeclarativeBase):
    pass

def generate_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"

class World(Base):
    __tablename__ = "mvp_worlds"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=lambda: generate_id("WORLD"))
    name: Mapped[str] = mapped_column(String(100), default="Genesis Sovereign World")
    is_paused: Mapped[bool] = mapped_column(Boolean, default=False)
    clock_tick: Mapped[int] = mapped_column(Integer, default=0)
    budget_limit_usd: Mapped[float] = mapped_column(Float, default=500.0)
    spent_budget_usd: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    companies: Mapped[List["Company"]] = relationship("Company", back_populates="world", cascade="all, delete-orphan")

class Company(Base):
    __tablename__ = "mvp_companies"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=lambda: generate_id("COMP"))
    world_id: Mapped[str] = mapped_column(String(32), ForeignKey("mvp_worlds.id"))
    name: Mapped[str] = mapped_column(String(100))
    ticker: Mapped[str] = mapped_column(String(20), unique=True)
    valuation_usd: Mapped[float] = mapped_column(Float, default=50000.0)
    treasury_balance: Mapped[float] = mapped_column(Float, default=5000.0)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    world: Mapped["World"] = relationship("World", back_populates="companies")
    agents: Mapped[List["Agent"]] = relationship("Agent", back_populates="company", cascade="all, delete-orphan")
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="company", cascade="all, delete-orphan")
    products: Mapped[List["Product"]] = relationship("Product", back_populates="company", cascade="all, delete-orphan")

class Agent(Base):
    __tablename__ = "mvp_agents"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=lambda: generate_id("AGENT"))
    company_id: Mapped[str] = mapped_column(String(32), ForeignKey("mvp_companies.id"))
    name: Mapped[str] = mapped_column(String(100))
    role: Mapped[str] = mapped_column(String(50))  # STRATEGIST, CODER, QA_AUDITOR
    skills_json: Mapped[str] = mapped_column(Text, default="[]")
    tasks_completed: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    company: Mapped["Company"] = relationship("Company", back_populates="agents")
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="assigned_agent")

class Task(Base):
    __tablename__ = "mvp_tasks"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=lambda: generate_id("TASK"))
    company_id: Mapped[str] = mapped_column(String(32), ForeignKey("mvp_companies.id"))
    assigned_agent_id: Mapped[Optional[str]] = mapped_column(String(32), ForeignKey("mvp_agents.id"), nullable=True)
    task_type: Mapped[str] = mapped_column(String(50))  # PROBLEM_DISCOVERY, CODE_SYNTHESIS, SANDBOX_TEST, FEEDBACK_PATCH
    payload_json: Mapped[str] = mapped_column(Text, default="{}")
    status: Mapped[str] = mapped_column(String(20), default="QUEUED")  # QUEUED, IN_PROGRESS, COMPLETED, FAILED
    result_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    company: Mapped["Company"] = relationship("Company", back_populates="tasks")
    assigned_agent: Mapped[Optional["Agent"]] = relationship("Agent", back_populates="tasks")

class Product(Base):
    __tablename__ = "mvp_products"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=lambda: generate_id("PROD"))
    company_id: Mapped[str] = mapped_column(String(32), ForeignKey("mvp_companies.id"))
    name: Mapped[str] = mapped_column(String(100))
    slug: Mapped[str] = mapped_column(String(100), unique=True)
    version: Mapped[str] = mapped_column(String(20), default="v1.0.0")
    code_content: Mapped[str] = mapped_column(Text)
    test_suite_content: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="STAGED")  # STAGED, TESTING, DEPLOYED, ROLLED_BACK
    test_exit_code: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    test_output: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    company: Mapped["Company"] = relationship("Company", back_populates="products")

class AuditLog(Base):
    __tablename__ = "mvp_audit_logs"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=lambda: generate_id("LOG"))
    world_id: Mapped[str] = mapped_column(String(32))
    actor_agent_id: Mapped[str] = mapped_column(String(32))
    action: Mapped[str] = mapped_column(String(50))
    details: Mapped[str] = mapped_column(Text)
    cost_usd: Mapped[float] = mapped_column(Float, default=0.0)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

def get_engine_and_session(db_path: str = "sqlite:///mvp_factory.db"):
    engine = create_engine(db_path, echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return engine, Session

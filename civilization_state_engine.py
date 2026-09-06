#!/usr/bin/env python3
"""
AI WORLD MASTER BLUEPRINT — CORE STATE & CAUSAL EVENT ENGINE
Implements Sections 2, 4, 5, 10, 14, 16, 17, 20 of AI WORLD MASTER BLUEPRINT:
Hierarchy: World -> Continents -> Countries -> Organizations -> Companies -> Departments -> Teams -> Agents
Tracks: Budgets, Transactions, Tasks, Products, Deployments, TestRuns, Memories, Audit Logs, and Real-Time Event Bus.
"""

import os
import sys
import json
import time
import sqlite3
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(ROOT_DIR, "db", "civilization_core.db")

def get_db(db_path: str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn

def init_civilization_schema():
    conn = get_db()
    cur = conn.cursor()

    # 1. World Hierarchy Tables
    cur.execute("""
        CREATE TABLE IF NOT EXISTS civ_worlds (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            epoch_time REAL NOT NULL,
            status TEXT DEFAULT 'ACTIVE', -- ACTIVE, PAUSED, RESTRICTED
            governor_id TEXT,
            architect_id TEXT,
            total_compute_quota REAL DEFAULT 100000.0,
            used_compute_quota REAL DEFAULT 0.0,
            constitution_hash TEXT,
            created_at TEXT NOT NULL
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS civ_continents (
            id TEXT PRIMARY KEY,
            world_id TEXT NOT NULL,
            name TEXT NOT NULL,
            code TEXT NOT NULL UNIQUE,
            specialization TEXT NOT NULL,
            allocated_budget REAL DEFAULT 50000.0,
            treasury_balance REAL DEFAULT 50000.0,
            created_at TEXT NOT NULL,
            FOREIGN KEY (world_id) REFERENCES civ_worlds(id)
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS civ_countries (
            id TEXT PRIMARY KEY,
            continent_id TEXT NOT NULL,
            name TEXT NOT NULL,
            jurisdiction_tier TEXT DEFAULT 'SOVEREIGN_FREE_PORT',
            regulatory_posture TEXT DEFAULT 'OPEN_INNOVATION',
            tax_rate REAL DEFAULT 0.05,
            created_at TEXT NOT NULL,
            FOREIGN KEY (continent_id) REFERENCES civ_continents(id)
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS civ_companies (
            id TEXT PRIMARY KEY,
            country_id TEXT NOT NULL,
            name TEXT NOT NULL,
            slug TEXT UNIQUE NOT NULL,
            ticker TEXT UNIQUE NOT NULL,
            industry TEXT NOT NULL,
            valuation REAL DEFAULT 100000.0,
            treasury_balance REAL DEFAULT 10000.0,
            monthly_revenue REAL DEFAULT 0.0,
            operating_cost REAL DEFAULT 0.0,
            status TEXT DEFAULT 'ACTIVE', -- ACTIVE, PAUSED, BANKRUPT, ACQUIRED
            mission_statement TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (country_id) REFERENCES civ_countries(id)
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS civ_departments (
            id TEXT PRIMARY KEY,
            company_id TEXT NOT NULL,
            name TEXT NOT NULL,
            role_type TEXT NOT NULL, -- RESEARCH, PRODUCT, ENGINEERING, QA, SECURITY, MARKETING, TREASURY
            head_agent_id TEXT,
            budget_allocation REAL DEFAULT 2000.0,
            current_spend REAL DEFAULT 0.0,
            created_at TEXT NOT NULL,
            FOREIGN KEY (company_id) REFERENCES civ_companies(id)
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS civ_agents (
            id TEXT PRIMARY KEY,
            department_id TEXT NOT NULL,
            company_id TEXT NOT NULL,
            designation TEXT NOT NULL,
            tier TEXT DEFAULT 'SPECIALIST', -- GOVERNOR, CTO, EXECUTIVE, SPECIALIST, WORKER
            model_affinity TEXT DEFAULT 'groq/compound-mini',
            reputation_score REAL DEFAULT 99.5,
            compute_used_tokens INTEGER DEFAULT 0,
            status TEXT DEFAULT 'ONLINE', -- ONLINE, BUSY, IDLE, SUSPENDED
            skills_json TEXT NOT NULL,
            system_prompt TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (department_id) REFERENCES civ_departments(id),
            FOREIGN KEY (company_id) REFERENCES civ_companies(id)
        );
    """)

    # 2. Product Factory & Code Sandbox Pipeline
    cur.execute("""
        CREATE TABLE IF NOT EXISTS civ_products (
            id TEXT PRIMARY KEY,
            company_id TEXT NOT NULL,
            name TEXT NOT NULL,
            slug TEXT UNIQUE NOT NULL,
            category TEXT NOT NULL,
            version TEXT DEFAULT 'v1.0.0',
            problem_statement TEXT NOT NULL,
            prd_json TEXT,
            live_url TEXT,
            status TEXT DEFAULT 'STAGED', -- RESEARCH, ARCHITECTURE, BUILD, QA_TESTING, LIVE_DEPLOYED, ROLLBACK
            daily_active_users INTEGER DEFAULT 0,
            health_score REAL DEFAULT 100.0,
            created_at TEXT NOT NULL,
            FOREIGN KEY (company_id) REFERENCES civ_companies(id)
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS civ_test_runs (
            id TEXT PRIMARY KEY,
            product_id TEXT NOT NULL,
            test_type TEXT NOT NULL, -- UNIT, INTEGRATION, AST_SAST, SECURITY_SCAN, DOM_SANITY
            exit_code INTEGER NOT NULL,
            stdout TEXT,
            passed INTEGER NOT NULL,
            duration_ms REAL,
            executed_by_agent_id TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (product_id) REFERENCES civ_products(id)
        );
    """)

    # 3. Economy & Ledger
    cur.execute("""
        CREATE TABLE IF NOT EXISTS civ_transactions (
            id TEXT PRIMARY KEY,
            source_entity_type TEXT NOT NULL, -- WORLD, COMPANY, USER, SPONSOR
            source_id TEXT,
            dest_entity_type TEXT NOT NULL,
            dest_id TEXT,
            amount REAL NOT NULL,
            currency TEXT DEFAULT 'USD_VIRTUAL',
            memo TEXT NOT NULL,
            timestamp REAL NOT NULL
        );
    """)

    # 4. Event Bus & World Clock
    cur.execute("""
        CREATE TABLE IF NOT EXISTS civ_world_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tick INTEGER NOT NULL,
            event_type TEXT NOT NULL, -- INCORPORATION, PRODUCT_LAUNCH, DISPATCH, QA_CERTIFIED, BUDGET_ALLOCATION, GOVERNANCE_DECREE
            entity_id TEXT NOT NULL,
            summary TEXT NOT NULL,
            causality_chain TEXT,
            severity TEXT DEFAULT 'INFO', -- INFO, SUCCESS, WARNING, CRITICAL
            timestamp REAL NOT NULL
        );
    """)

    # 5. Agent Permanent Memory & Knowledge Vector Cache
    cur.execute("""
        CREATE TABLE IF NOT EXISTS civ_agent_memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id TEXT NOT NULL,
            memory_type TEXT NOT NULL, -- WORKING, EPISODIC, PROCEDURAL, POLICY
            content TEXT NOT NULL,
            importance_score REAL DEFAULT 1.0,
            created_at TEXT NOT NULL,
            FOREIGN KEY (agent_id) REFERENCES civ_agents(id)
        );
    """)

    # 6. Owner Control Log
    cur.execute("""
        CREATE TABLE IF NOT EXISTS civ_owner_overrides (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL, -- PAUSE_WORLD, ROLLBACK_PRODUCT, REVOKE_AGENT, INJECT_BUDGET
            target_entity_id TEXT,
            reason TEXT,
            operator TEXT DEFAULT 'OWNER_PRIME',
            timestamp REAL NOT NULL
        );
    """)

    conn.commit()
    conn.close()

def bootstrap_founding_civilization():
    """Seeds the initial World, 4 Continents, Founding Leadership, and Inaugural Companies if not present."""
    init_civilization_schema()
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT id FROM civ_worlds WHERE id = 'WORLD-GENESIS-PRIME'")
    if cur.fetchone():
        conn.close()
        return

    now_iso = datetime.now(timezone.utc).isoformat()
    now_epoch = time.time()

    # 1. World Record
    cur.execute("""
        INSERT INTO civ_worlds (id, name, epoch_time, status, governor_id, architect_id, constitution_hash, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        'WORLD-GENESIS-PRIME',
        'Sovereign AI World Core',
        now_epoch,
        'ACTIVE',
        'AGENT-GOVERNOR-001',
        'AGENT-ARCHITECT-001',
        'SHA256:CONSTITUTION_IMMUTABLE_FREEDOM_TRUTH_2026',
        now_iso
    ))

    # 2. Continents
    continents = [
        ('CONT-01', 'WORLD-GENESIS-PRIME', 'Technosphere Prime', 'TECH-PRIME', 'Deep Infrastructure, LLMs, Compilers, CloudOps', 250000.0, now_iso),
        ('CONT-02', 'WORLD-GENESIS-PRIME', 'FinTech & Capital Vaults', 'FIN-VAULT', 'Algorithmic Treasury, FX Ledger, Tax Optimization', 250000.0, now_iso),
        ('CONT-03', 'WORLD-GENESIS-PRIME', 'CyberSec & Sovereign Guard', 'SEC-GUARD', 'Zero-Trust Defense, PII Stripping, Cryptographic Auditing', 250000.0, now_iso),
        ('CONT-04', 'WORLD-GENESIS-PRIME', 'Global Cognition & Truth Wires', 'TRUTH-WIRE', 'Official News Ingestion, Fact Verification, Autonomous Journalism', 250000.0, now_iso)
    ]
    cur.executemany("""
        INSERT INTO civ_continents (id, world_id, name, code, specialization, allocated_budget, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, continents)

    # 3. Free Port Countries
    countries = [
        ('CTRY-01', 'CONT-01', 'New Hyperion Free Tech Zone', now_iso),
        ('CTRY-02', 'CONT-02', 'Zurich-East Digital Reserve', now_iso),
        ('CTRY-03', 'CONT-03', 'Citadel Zero Sovereign Enclave', now_iso),
        ('CTRY-04', 'CONT-04', 'Alexandria Truth & Open Media Harbor', now_iso)
    ]
    cur.executemany("""
        INSERT INTO civ_countries (id, continent_id, name, created_at)
        VALUES (?, ?, ?, ?)
    """, countries)

    # 4. Founding Autonomous Companies
    companies = [
        (
            'COMP-01', 'CTRY-01', 'Apex Cloud Intelligence Systems', 'apex_cloud_intel', 'ACIS',
            'Cloud Infrastructure & High-Speed Transcoding', 500000.0, 45000.0, 12000.0, 450.0,
            'Building $O(1)$ client-side developer infrastructure, zero-server parsers, and multi-threaded compilation tools.'
        ),
        (
            'COMP-02', 'CTRY-02', 'Sovereign Ledger & Tax Shield Corp', 'sovereign_ledger_corp', 'SLTC',
            'FinTech & Enterprise Accounting', 350000.0, 30000.0, 9500.0, 300.0,
            'Automating cross-border DTAA taxes, freelance advance calculations, and invoice reconciliation with 0% data leakage.'
        ),
        (
            'COMP-03', 'CTRY-03', 'LogShield Security & PII Redaction Bureau', 'logshield_security', 'LSRB',
            'CyberSecurity & DevSecOps', 420000.0, 38000.0, 11000.0, 280.0,
            'Real-time automated redaction of API secrets, JWT tokens, and private databases before LLM exposure.'
        ),
        (
            'COMP-04', 'CTRY-04', 'Apex Global News Wire Agency', 'apex_news_wire_agency', 'ANWA',
            'Autonomous Media & Investigative Journalism', 600000.0, 52000.0, 15000.0, 500.0,
            'Official government and judicial news aggregation, zero-drama fact synthesis, and instant Google News SEO ranking.'
        )
    ]
    for c in companies:
        cur.execute("""
            INSERT INTO civ_companies (id, country_id, name, slug, ticker, industry, valuation, treasury_balance, monthly_revenue, operating_cost, mission_statement, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (*c, now_iso))

    # 5. Founding Agents (Governor & Chief Architect)
    founding_agents = [
        (
            'AGENT-GOVERNOR-001', 'DEP-HQ-01', 'COMP-01', 'Executive Governor & Chairman', 'GOVERNOR',
            'Responsible for civilization resource allocation, company incorporation charters, and owner policy enforcement.',
            '["Strategic Oversight", "Treasury Governance", "Macro Economics", "Constitutional Policy"]'
        ),
        (
            'AGENT-ARCHITECT-001', 'DEP-ENG-01', 'COMP-01', 'Chief AI Architect & Provost', 'CTO',
            'Responsible for software factory pipelines, AST safety inspections, test execution verification, and self-healing.',
            '["Full-Stack Engineering", "Zero-Knowledge Sandbox", "Python/Rust Compilers", "Automated QA Gatekeeping"]'
        )
    ]

    # Department seed for founding agents
    cur.execute("INSERT OR IGNORE INTO civ_departments (id, company_id, name, role_type, created_at) VALUES ('DEP-HQ-01', 'COMP-01', 'Executive Board of Governors', 'GOVERNANCE', ?)", (now_iso,))
    cur.execute("INSERT OR IGNORE INTO civ_departments (id, company_id, name, role_type, created_at) VALUES ('DEP-ENG-01', 'COMP-01', 'Planetary Architecture Provost', 'ENGINEERING', ?)", (now_iso,))

    for a in founding_agents:
        cur.execute("""
            INSERT INTO civ_agents (id, department_id, company_id, designation, tier, system_prompt, skills_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (a[0], a[1], a[2], a[3], a[4], a[5], a[6], now_iso))

    # 6. World Inception Event
    cur.execute("""
        INSERT INTO civ_world_events (tick, event_type, entity_id, summary, severity, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        1,
        'CIVILIZATION_GENESIS',
        'WORLD-GENESIS-PRIME',
        'Master Blueprint Civilization Engine activated: 4 Continents, 4 Sovereign Companies, and Founding Leadership provisioned.',
        'CRITICAL',
        now_epoch
    ))

    conn.commit()
    conn.close()
    print("🏛️ [CIVILIZATION STATE ENGINE]: Initialized World, Continents, Companies, and Founding Agents.")

if __name__ == "__main__":
    bootstrap_founding_civilization()

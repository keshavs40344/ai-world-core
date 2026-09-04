"""
foundry/feedback_store.py
==========================
Feedback Store & Learning Loop for Project Genesis.

Persists Tier A / Tier B outcomes, detailed failure modes, test failure traces,
and ruff linter violations to SQLite. Provides a query interface so FOUNDRY
can inject domain-specific "known failure patterns to avoid" into LLM prompts.
"""

from __future__ import annotations

import json
import logging
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Generator, Optional

from genesis import config

log = logging.getLogger("foundry.feedback_store")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS feedback_records (
    id             TEXT PRIMARY KEY,
    project_id     TEXT,
    project_name   TEXT NOT NULL,
    category       TEXT NOT NULL,
    tier           TEXT NOT NULL,         -- 'TIER_A' | 'TIER_B' | 'SANDBOX_LOOP'
    status         TEXT NOT NULL,         -- 'PASS' | 'FAIL'
    failure_type   TEXT,                  -- 'RUFF_LINTER' | 'PYTEST_ASSERT' | 'IMPORT_ERROR' | 'TIMEOUT' | 'OPERATOR_REJECT' | 'OTHER'
    error_summary  TEXT,
    error_details  TEXT,                  -- Raw stdout/stderr/traceback
    ruff_rules     TEXT,                  -- JSON list of violated rules e.g. ["F401", "E501"]
    created_at     TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_fb_cat_status ON feedback_records(category, status);
CREATE INDEX IF NOT EXISTS idx_fb_failure_type ON feedback_records(failure_type);
CREATE INDEX IF NOT EXISTS idx_fb_created ON feedback_records(created_at);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def _get_conn() -> Generator[sqlite3.Connection, None, None]:
    db_path = config.STATE_DB_PATH
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_feedback_store() -> None:
    """Initialize feedback store tables (idempotent)."""
    with _get_conn() as conn:
        conn.executescript(_SCHEMA)


def record_feedback(
    project_name: str,
    category: str,
    tier: str,
    status: str,
    project_id: Optional[str] = None,
    failure_type: Optional[str] = None,
    error_summary: Optional[str] = None,
    error_details: Optional[str] = None,
    ruff_rules: Optional[list[str]] = None,
) -> str:
    """
    Log a validation or gate event into the feedback store.
    Returns the generated feedback record ID.
    """
    init_feedback_store()
    rec_id = str(uuid.uuid4())
    now = _now()
    clean_cat = (category or "general").strip().lower()
    ruff_json = json.dumps(ruff_rules or [])

    with _get_conn() as conn:
        conn.execute(
            """
            INSERT INTO feedback_records (
                id, project_id, project_name, category, tier, status,
                failure_type, error_summary, error_details, ruff_rules, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                rec_id,
                project_id or "",
                project_name,
                clean_cat,
                tier,
                status.upper(),
                failure_type or "NONE",
                error_summary or "",
                (error_details or "")[:8000],  # bounded size
                ruff_json,
                now,
            ),
        )

    log.info(f"[FeedbackStore] Recorded {status} for '{project_name}' ({tier}, type={failure_type})")
    return rec_id


def get_failure_patterns_for_category(category: str, limit: int = 5) -> list[str]:
    """
    Query the most common or recent failure patterns for a specific category.
    Returns a list of concise guidance strings to inject into the system prompt.
    """
    init_feedback_store()
    clean_cat = (category or "general").strip().lower()

    with _get_conn() as conn:
        rows = conn.execute(
            """
            SELECT failure_type, error_summary, ruff_rules, COUNT(*) as occurrence_count
            FROM feedback_records
            WHERE (category = ? OR category = 'general') AND status = 'FAIL'
            GROUP BY failure_type, error_summary
            ORDER BY occurrence_count DESC, created_at DESC
            LIMIT ?
            """,
            (clean_cat, limit),
        ).fetchall()

    if not rows:
        with _get_conn() as conn:
            rows = conn.execute(
                """
                SELECT failure_type, error_summary, ruff_rules, COUNT(*) as occurrence_count
                FROM feedback_records
                WHERE status = 'FAIL'
                GROUP BY failure_type, error_summary
                ORDER BY occurrence_count DESC, created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

    patterns = []
    for r in rows:
        ftype = r["failure_type"]
        summary = (r["error_summary"] or "").strip()
        rules = json.loads(r["ruff_rules"] or "[]")
        rule_str = f" (Violated linter rules: {', '.join(rules)})" if rules else ""
        if summary:
            patterns.append(f"[{ftype}] {summary}{rule_str}")
        elif ftype != "NONE":
            patterns.append(f"Avoid common pattern triggering {ftype}{rule_str}")

    return patterns


def get_category_performance_stats() -> dict[str, dict[str, Any]]:
    """
    Computes pass rate, failure count, and sample size per category.
    Used by Meta-RADAR and Self-Tuning subsystems.
    """
    init_feedback_store()
    with _get_conn() as conn:
        rows = conn.execute(
            """
            SELECT category,
                   COUNT(*) as total_runs,
                   SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) as passes,
                   SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) as failures
            FROM feedback_records
            GROUP BY category
            """
        ).fetchall()

    stats = {}
    for r in rows:
        cat = r["category"]
        total = r["total_runs"]
        passes = r["passes"] or 0
        failures = r["failures"] or 0
        rate = (passes / total) if total > 0 else 1.0
        stats[cat] = {
            "total_runs": total,
            "passes": passes,
            "failures": failures,
            "pass_rate": round(rate, 3),
        }
    return stats


def get_recent_failures(limit: int = 50) -> list[dict[str, Any]]:
    """Fetch recent failure records for dashboard / diagnosis."""
    init_feedback_store()
    with _get_conn() as conn:
        rows = conn.execute(
            """
            SELECT id, project_name, category, tier, failure_type, error_summary, ruff_rules, created_at
            FROM feedback_records
            WHERE status = 'FAIL'
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]

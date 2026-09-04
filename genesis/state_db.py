"""
genesis/state_db.py
===================
SQLite-backed state store for Project Genesis.

Uses WAL (Write-Ahead Logging) mode for safe concurrent reads from
multiple processes. All writes are serialised through a single connection
per process — this is intentional to avoid contention on Windows.
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Generator, Optional

from genesis import config as _genesis_config


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

_SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS tasks (
    id           TEXT PRIMARY KEY,
    manifest_ref TEXT,                  -- path to project_manifest.json snapshot
    project_name TEXT NOT NULL,
    status       TEXT NOT NULL DEFAULT 'PENDING',
                 -- PENDING | IN_PROGRESS | PASSED | CIRCUIT_BROKEN | RELEASED | REJECTED
    attempts     INTEGER NOT NULL DEFAULT 0,
    priority     INTEGER NOT NULL DEFAULT 5,   -- lower = higher priority
    payload      TEXT,                  -- JSON blob: manifest data
    error_log    TEXT,                  -- last error / stack trace
    created_at   TEXT NOT NULL,
    updated_at   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS cycles (
    id           TEXT PRIMARY KEY,
    started_at   TEXT NOT NULL,
    completed_at TEXT,
    outcome      TEXT,                  -- SUCCESS | PARTIAL | FAILED
    tasks_run    INTEGER DEFAULT 0,
    tasks_passed INTEGER DEFAULT 0,
    notes        TEXT
);

CREATE TABLE IF NOT EXISTS digest_log (
    id           TEXT PRIMARY KEY,
    level        TEXT NOT NULL DEFAULT 'INFO',  -- INFO | WARN | ERROR
    category     TEXT,                          -- TIER_A | TIER_B | RADAR | FOUNDRY | VAULT
    message      TEXT NOT NULL,
    payload      TEXT,                          -- optional JSON
    created_at   TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_tasks_status   ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority, created_at);
CREATE INDEX IF NOT EXISTS idx_digest_created ON digest_log(created_at);
"""


# ---------------------------------------------------------------------------
# Connection management
# ---------------------------------------------------------------------------

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id() -> str:
    return str(uuid.uuid4())


@contextmanager
def _get_conn() -> Generator[sqlite3.Connection, None, None]:
    db_path = _genesis_config.STATE_DB_PATH          # read dynamically — supports test monkeypatching
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


def init_db() -> None:
    """Initialise the database schema (idempotent)."""
    with _get_conn() as conn:
        conn.executescript(_SCHEMA)


# ---------------------------------------------------------------------------
# Task CRUD
# ---------------------------------------------------------------------------

def enqueue_task(
    project_name: str,
    payload: dict[str, Any],
    priority: int = 5,
    manifest_ref: Optional[str] = None,
) -> str:
    """Add a new task to the backlog. Returns the task ID."""
    task_id = _new_id()
    now = _now()
    with _get_conn() as conn:
        conn.execute(
            """
            INSERT INTO tasks
                (id, manifest_ref, project_name, status, attempts, priority,
                 payload, created_at, updated_at)
            VALUES (?, ?, ?, 'PENDING', 0, ?, ?, ?, ?)
            """,
            (task_id, manifest_ref, project_name, priority,
             json.dumps(payload), now, now),
        )
    return task_id


def claim_next_task() -> Optional[dict[str, Any]]:
    """
    Atomically claim the highest-priority PENDING task.
    Returns the task row as a dict, or None if the queue is empty.
    """
    with _get_conn() as conn:
        row = conn.execute(
            """
            SELECT * FROM tasks
            WHERE  status = 'PENDING'
            ORDER  BY priority ASC, created_at ASC
            LIMIT  1
            """
        ).fetchone()
        if row is None:
            return None
        task = dict(row)
        now = _now()
        conn.execute(
            "UPDATE tasks SET status='IN_PROGRESS', updated_at=? WHERE id=?",
            (now, task["id"]),
        )
        # Reflect the update in the returned dict
        task["status"] = "IN_PROGRESS"
        task["updated_at"] = now
    if task.get("payload"):
        task["payload"] = json.loads(task["payload"])
    return task


def update_task_status(
    task_id: str,
    status: str,
    error_log: Optional[str] = None,
    increment_attempts: bool = False,
) -> None:
    """Update a task's status and optional error log."""
    with _get_conn() as conn:
        if increment_attempts:
            conn.execute(
                """
                UPDATE tasks
                SET status=?, error_log=?, attempts=attempts+1, updated_at=?
                WHERE id=?
                """,
                (status, error_log, _now(), task_id),
            )
        else:
            conn.execute(
                """
                UPDATE tasks
                SET status=?, error_log=?, updated_at=?
                WHERE id=?
                """,
                (status, error_log, _now(), task_id),
            )


def get_task(task_id: str) -> Optional[dict[str, Any]]:
    with _get_conn() as conn:
        row = conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
    if row is None:
        return None
    task = dict(row)
    if task.get("payload"):
        task["payload"] = json.loads(task["payload"])
    return task


def list_tasks(status: Optional[str] = None, limit: int = 50) -> list[dict[str, Any]]:
    with _get_conn() as conn:
        if status:
            rows = conn.execute(
                "SELECT * FROM tasks WHERE status=? ORDER BY priority, created_at LIMIT ?",
                (status, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM tasks ORDER BY priority, created_at LIMIT ?",
                (limit,),
            ).fetchall()
    result = []
    for row in rows:
        t = dict(row)
        if t.get("payload"):
            t["payload"] = json.loads(t["payload"])
        result.append(t)
    return result


# ---------------------------------------------------------------------------
# Cycle CRUD
# ---------------------------------------------------------------------------

def start_cycle() -> str:
    cycle_id = _new_id()
    with _get_conn() as conn:
        conn.execute(
            "INSERT INTO cycles (id, started_at) VALUES (?, ?)",
            (cycle_id, _now()),
        )
    return cycle_id


def finish_cycle(
    cycle_id: str,
    outcome: str,
    tasks_run: int = 0,
    tasks_passed: int = 0,
    notes: Optional[str] = None,
) -> None:
    with _get_conn() as conn:
        conn.execute(
            """
            UPDATE cycles
            SET completed_at=?, outcome=?, tasks_run=?, tasks_passed=?, notes=?
            WHERE id=?
            """,
            (_now(), outcome, tasks_run, tasks_passed, notes, cycle_id),
        )


# ---------------------------------------------------------------------------
# Digest log
# ---------------------------------------------------------------------------

def log_event(
    message: str,
    level: str = "INFO",
    category: Optional[str] = None,
    payload: Optional[dict[str, Any]] = None,
) -> None:
    with _get_conn() as conn:
        conn.execute(
            """
            INSERT INTO digest_log (id, level, category, message, payload, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                _new_id(),
                level,
                category,
                message,
                json.dumps(payload) if payload else None,
                _now(),
            ),
        )


def get_recent_events(hours: float = 24.0, limit: int = 200) -> list[dict[str, Any]]:
    from datetime import timedelta
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM digest_log WHERE created_at >= ? ORDER BY created_at DESC LIMIT ?",
            (cutoff, limit),
        ).fetchall()
    result = []
    for row in rows:
        e = dict(row)
        if e.get("payload"):
            e["payload"] = json.loads(e["payload"])
        result.append(e)
    return result

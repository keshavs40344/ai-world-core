"""
foundry/prompt_registry.py
===========================
Prompt & Strategy Versioning System for Project Genesis.

Treats generation prompts as first-class, versioned database artifacts.
Tracks:
  - First-try pass rate (passed without self-healing retries)
  - Number of test retries needed
  - Tier B operator approval rate
  - Auto-promotion of the best-performing prompt version per category
"""

from __future__ import annotations

import logging
import sqlite3
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Generator, Optional

from genesis import config

log = logging.getLogger("foundry.prompt_registry")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS prompt_versions (
    id                TEXT PRIMARY KEY,
    role              TEXT NOT NULL,         -- 'core_engineer' | 'test_engineer'
    category          TEXT NOT NULL,         -- 'general' | 'developer_tools' | etc.
    version_tag       TEXT NOT NULL,         -- 'v1.0.0', 'v1.1.0-concise', etc.
    template_text     TEXT NOT NULL,
    is_active         INTEGER NOT NULL DEFAULT 0,
    total_runs        INTEGER NOT NULL DEFAULT 0,
    first_try_passes  INTEGER NOT NULL DEFAULT 0,
    retries_needed    INTEGER NOT NULL DEFAULT 0,
    tier_b_approvals  INTEGER NOT NULL DEFAULT 0,
    created_at        TEXT NOT NULL,
    updated_at        TEXT NOT NULL,
    UNIQUE(role, category, version_tag)
);

CREATE INDEX IF NOT EXISTS idx_prompt_active ON prompt_versions(role, category, is_active);
"""

_DEFAULT_CORE_PROMPT = """\
You are a senior Python engineer at an autonomous open-source foundry.
Your task is to implement a complete, production-quality Python project
based on the specification below. Requirements:
- Pure Python 3.11+ with type hints throughout
- Follow PEP 8 and keep the code concise and clean (< 200 lines total)
- The main entry point must be `src/main.py`
- Include `requirements.txt` (keep dependencies minimal or empty if standard library suffices)
- Include `README.md` with: overview, installation, and usage examples

PROJECT SPECIFICATION:
{manifest_json}

{failure_guidance}

OUTPUT FORMAT:
Return a JSON object where each key is a file path (relative to project root)
and each value is the complete file content as a string. Example:
{{
  "src/main.py": "...",
  "requirements.txt": "...",
  "README.md": "..."
}}
CRITICAL: The JSON keys must ONLY be relative file paths (e.g. 'src/main.py', 'requirements.txt').
Do NOT output manifest fields (such as 'name', 'goals', 'category') as keys.
Return ONLY the JSON object — no prose, no markdown fences.
"""

_DEFAULT_TEST_PROMPT = """\
You are a test automation engineer. Given the following project source code
and specification, write a concise, robust pytest test suite (< 60 lines).

Requirements:
- Use pytest with standard unit tests
- Use only standard library + pytest — no external dependencies
- The test file must be `tests/test_main.py`

PROJECT SPECIFICATION:
{manifest_json}

{failure_guidance}

SOURCE CODE:
{source_code}

Return a JSON object mapping file paths to file content (e.g. {{"tests/test_main.py": "..."}}).
Return ONLY the JSON object.
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


def init_prompt_registry() -> None:
    """Initialize tables and populate default active prompt templates if empty."""
    with _get_conn() as conn:
        conn.executescript(_SCHEMA)
        # Check core_engineer default
        row_core = conn.execute(
            "SELECT id FROM prompt_versions WHERE role='core_engineer' AND category='general'"
        ).fetchone()
        if not row_core:
            conn.execute(
                """
                INSERT INTO prompt_versions
                    (id, role, category, version_tag, template_text, is_active, created_at, updated_at)
                VALUES (?, 'core_engineer', 'general', 'v1.0.0-baseline', ?, 1, ?, ?)
                """,
                (str(uuid.uuid4()), _DEFAULT_CORE_PROMPT, _now(), _now()),
            )

        # Check test_engineer default
        row_test = conn.execute(
            "SELECT id FROM prompt_versions WHERE role='test_engineer' AND category='general'"
        ).fetchone()
        if not row_test:
            conn.execute(
                """
                INSERT INTO prompt_versions
                    (id, role, category, version_tag, template_text, is_active, created_at, updated_at)
                VALUES (?, 'test_engineer', 'general', 'v1.0.0-baseline', ?, 1, ?, ?)
                """,
                (str(uuid.uuid4()), _DEFAULT_TEST_PROMPT, _now(), _now()),
            )


@dataclass
class PromptVersion:
    id: str
    role: str
    category: str
    version_tag: str
    template_text: str
    is_active: bool
    total_runs: int
    first_try_passes: int
    retries_needed: int
    tier_b_approvals: int

    @property
    def pass_rate(self) -> float:
        return (self.first_try_passes / self.total_runs) if self.total_runs > 0 else 0.0

    @property
    def approval_rate(self) -> float:
        return (self.tier_b_approvals / self.total_runs) if self.total_runs > 0 else 0.0


def get_active_prompt(role: str, category: str = "general") -> PromptVersion:
    """
    Fetch the currently active prompt for a given role and category.
    Falls back to 'general' category if no category-specific version exists.
    """
    init_prompt_registry()
    clean_cat = (category or "general").strip().lower()

    with _get_conn() as conn:
        # Category-specific active prompt
        row = conn.execute(
            """
            SELECT * FROM prompt_versions
            WHERE role = ? AND category = ? AND is_active = 1
            LIMIT 1
            """,
            (role, clean_cat),
        ).fetchone()

        if not row:
            # Fallback to general category active prompt
            row = conn.execute(
                """
                SELECT * FROM prompt_versions
                WHERE role = ? AND category = 'general' AND is_active = 1
                LIMIT 1
                """,
                (role,),
            ).fetchone()

    if row:
        return PromptVersion(
            id=row["id"],
            role=row["role"],
            category=row["category"],
            version_tag=row["version_tag"],
            template_text=row["template_text"],
            is_active=bool(row["is_active"]),
            total_runs=row["total_runs"],
            first_try_passes=row["first_try_passes"],
            retries_needed=row["retries_needed"],
            tier_b_approvals=row["tier_b_approvals"],
        )

    # In-memory baseline fallback
    template = _DEFAULT_CORE_PROMPT if role == "core_engineer" else _DEFAULT_TEST_PROMPT
    return PromptVersion(
        id="fallback",
        role=role,
        category="general",
        version_tag="v1.0.0-fallback",
        template_text=template,
        is_active=True,
        total_runs=0,
        first_try_passes=0,
        retries_needed=0,
        tier_b_approvals=0,
    )


def register_prompt(
    role: str,
    template_text: str,
    version_tag: str,
    category: str = "general",
    set_active: bool = False,
) -> str:
    """Register a new candidate prompt version."""
    init_prompt_registry()
    p_id = str(uuid.uuid4())
    now = _now()
    clean_cat = (category or "general").strip().lower()

    with _get_conn() as conn:
        if set_active:
            conn.execute(
                "UPDATE prompt_versions SET is_active = 0 WHERE role = ? AND category = ?",
                (role, clean_cat),
            )

        conn.execute(
            """
            INSERT INTO prompt_versions
                (id, role, category, version_tag, template_text, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (p_id, role, clean_cat, version_tag, template_text, 1 if set_active else 0, now, now),
        )
    log.info(f"[PromptRegistry] Registered prompt version '{version_tag}' for {role} [{clean_cat}]")
    return p_id


def record_prompt_outcome(
    version_id: str,
    passed_first_try: bool,
    retries: int = 0,
    tier_b_approved: bool = False,
) -> None:
    """Record execution telemetry for a prompt version."""
    init_prompt_registry()
    now = _now()
    with _get_conn() as conn:
        conn.execute(
            """
            UPDATE prompt_versions
            SET total_runs = total_runs + 1,
                first_try_passes = first_try_passes + ?,
                retries_needed = retries_needed + ?,
                tier_b_approvals = tier_b_approvals + ?,
                updated_at = ?
            WHERE id = ?
            """,
            (1 if passed_first_try else 0, retries, 1 if tier_b_approved else 0, now, version_id),
        )


def auto_promote_best_version(role: str, category: str = "general", min_sample: int = 5) -> Optional[str]:
    """
    Evaluates candidate prompt versions with >= min_sample runs.
    Promotes the version with the highest (first_try_pass_rate * 0.7 + tier_b_rate * 0.3).
    Returns the newly promoted version_tag, or None if no change.
    """
    init_prompt_registry()
    clean_cat = (category or "general").strip().lower()

    with _get_conn() as conn:
        rows = conn.execute(
            """
            SELECT * FROM prompt_versions
            WHERE role = ? AND category = ? AND total_runs >= ?
            """,
            (role, clean_cat, min_sample),
        ).fetchall()

        if not rows:
            return None

        best_score = -1.0
        best_row = None
        current_active = None

        for r in rows:
            if r["is_active"] == 1:
                current_active = r
            runs = r["total_runs"]
            first_pass_rate = r["first_try_passes"] / runs
            approval_rate = r["tier_b_approvals"] / runs
            score = (first_pass_rate * 0.7) + (approval_rate * 0.3)
            if score > best_score:
                best_score = score
                best_row = r

        if best_row and (current_active is None or best_row["id"] != current_active["id"]):
            conn.execute(
                "UPDATE prompt_versions SET is_active = 0 WHERE role = ? AND category = ?",
                (role, clean_cat),
            )
            conn.execute(
                "UPDATE prompt_versions SET is_active = 1, updated_at = ? WHERE id = ?",
                (_now(), best_row["id"]),
            )
            log.info(f"[PromptRegistry] Promoted '{best_row['version_tag']}' to active for {role} (score: {best_score:.2f})")
            return best_row["version_tag"]

    return None


def list_prompt_versions(role: Optional[str] = None) -> list[dict[str, Any]]:
    """List all registered prompt versions and their metrics."""
    init_prompt_registry()
    with _get_conn() as conn:
        if role:
            rows = conn.execute(
                "SELECT * FROM prompt_versions WHERE role = ? ORDER BY category, is_active DESC, created_at DESC",
                (role,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM prompt_versions ORDER BY role, category, is_active DESC, created_at DESC"
            ).fetchall()
    return [dict(r) for r in rows]

"""
dashboard/app.py
================
Project Genesis — Operator Dashboard (Streamlit)

Provides a real-time view of the Genesis engine:
  - Current engine status (cycles, tasks, errors)
  - Backlog queue (pending / in-progress / passed / broken)
  - Tier B release cards awaiting Operator sign-off
  - Daily digest viewer
  - Manual controls: trigger a dry-run cycle, open release gate

Run with:
    streamlit run dashboard/app.py
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="⚗️ Genesis Dashboard",
    page_icon="⚗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Add project root to sys.path ───────────────────────────────────────────
import sys
_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

from genesis import config
from genesis.state_db import init_db, list_tasks, get_recent_events
from governance.digest_logger import DigestLogger


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _status_badge(status: str) -> str:
    badges = {
        "PENDING":         "🟡",
        "IN_PROGRESS":     "🔵",
        "PASSED":          "✅",
        "CIRCUIT_BROKEN":  "💥",
        "RELEASED":        "🚀",
        "REJECTED":        "❌",
        "PENDING_RELEASE": "🔒",
        "TIMEOUT":         "⏰",
    }
    return f"{badges.get(status, '⚪')} {status}"


def _pending_release_cards() -> list[Path]:
    return sorted(config.RELEASE_GATE_DIR.glob("*.PENDING.md"))


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("⚗️ Genesis Control")
    st.caption(f"Local time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.divider()

    st.subheader("Engine")
    if st.button("🔄 Refresh Dashboard"):
        st.rerun()

    if st.button("🧪 Trigger Dry-Run Cycle"):
        import subprocess
        subprocess.Popen(
            [sys.executable, "-m", "genesis.controller", "--dry-run"],
            cwd=str(_ROOT),
        )
        st.success("Dry-run cycle launched! Check logs for output.")

    st.divider()
    st.subheader("Vault Stats")
    try:
        from vault.vector_store import VectorStore
        vs = VectorStore()
        stats = vs.stats()
        st.metric("Code Helpers", stats["code_helpers"])
        st.metric("Project Docs", stats["project_docs"])
        st.metric("Failure Archive", stats["failure_archive"])
    except Exception as e:
        st.warning(f"ChromaDB offline: {e}")

    st.divider()
    st.caption("Project Genesis v1.0.0 | Local-First Mode")


# ---------------------------------------------------------------------------
# Main tabs
# ---------------------------------------------------------------------------

init_db()

tab_tasks, tab_tier_b, tab_digest, tab_config = st.tabs([
    "📋 Task Queue",
    "🔒 Release Gate",
    "📊 Daily Digest",
    "⚙️ Config",
])


# ── Tab 1: Task Queue ──────────────────────────────────────────────────────
with tab_tasks:
    st.header("📋 Task Queue")

    col1, col2, col3, col4 = st.columns(4)
    all_tasks = list_tasks(limit=200)
    status_counts = {}
    for t in all_tasks:
        s = t["status"]
        status_counts[s] = status_counts.get(s, 0) + 1

    col1.metric("Pending",        status_counts.get("PENDING", 0))
    col2.metric("In Progress",    status_counts.get("IN_PROGRESS", 0))
    col3.metric("Passed",         status_counts.get("PASSED", 0))
    col4.metric("Circuit Broken", status_counts.get("CIRCUIT_BROKEN", 0))

    st.divider()

    status_filter = st.selectbox(
        "Filter by status",
        ["ALL", "PENDING", "IN_PROGRESS", "PASSED", "CIRCUIT_BROKEN",
         "RELEASED", "REJECTED", "PENDING_RELEASE"],
    )

    filtered = all_tasks if status_filter == "ALL" else [
        t for t in all_tasks if t["status"] == status_filter
    ]

    if not filtered:
        st.info("No tasks match the selected filter.")
    else:
        for task in filtered[:50]:
            with st.expander(
                f"{_status_badge(task['status'])} — **{task['project_name']}** "
                f"(attempts: {task['attempts']})"
            ):
                col_l, col_r = st.columns(2)
                col_l.write(f"**ID:** `{task['id'][:16]}…`")
                col_r.write(f"**Priority:** {task['priority']}")
                col_l.write(f"**Created:** {task['created_at'][:19]}")
                col_r.write(f"**Updated:** {task['updated_at'][:19]}")
                if task.get("error_log"):
                    st.code(task["error_log"][:500], language="text")


# ── Tab 2: Release Gate ────────────────────────────────────────────────────
with tab_tier_b:
    st.header("🔒 Tier B Release Gate")
    cards = _pending_release_cards()

    if not cards:
        st.success("✅ No pending release cards. All clear.")
    else:
        st.warning(f"{len(cards)} release card(s) awaiting Operator decision.")
        for card in cards:
            project_id = card.stem.replace(".PENDING", "")
            content = card.read_text(encoding="utf-8")
            with st.expander(f"🔒 {project_id[:16]}…"):
                st.markdown(content)
                c1, c2 = st.columns(2)
                if c1.button(f"✅ AUTHORIZE {project_id[:8]}", key=f"auth_{project_id}"):
                    (config.RELEASE_GATE_DIR / f"{project_id}.AUTHORIZE").touch()
                    st.success("Authorization file created. Engine will detect and proceed.")
                if c2.button(f"❌ REJECT & PURGE {project_id[:8]}", key=f"rej_{project_id}"):
                    (config.RELEASE_GATE_DIR / f"{project_id}.REJECT").touch()
                    st.error("Rejection file created. Engine will purge the project.")


# ── Tab 3: Daily Digest ────────────────────────────────────────────────────
with tab_digest:
    st.header("📊 Daily Digest")

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    digest_path = config.LOGS_DIR / f"digest_{today}.md"

    if digest_path.exists():
        st.markdown(digest_path.read_text(encoding="utf-8"))
    else:
        if st.button("📝 Generate Today's Digest"):
            dl = DigestLogger()
            summary = dl.generate_daily_summary()
            st.markdown(summary)
        else:
            st.info("No digest for today yet. Click above to generate.")

    st.divider()
    st.subheader("Recent Events (last 24h)")
    events = get_recent_events(hours=24, limit=100)
    if events:
        for e in events[:30]:
            level_icon = {"INFO": "ℹ️", "WARN": "⚠️", "ERROR": "🔴"}.get(e["level"], "•")
            st.text(f"{level_icon} [{e['created_at'][:19]}] [{e.get('category','?')}] {e['message']}")
    else:
        st.info("No recent events.")


# ── Tab 4: Config ──────────────────────────────────────────────────────────
with tab_config:
    st.header("⚙️ Active Configuration")
    cfg_data = {
        "Ollama Host":          config.OLLAMA_HOST,
        "Primary Model":        config.OLLAMA_PRIMARY_MODEL,
        "Fallback Models":      ", ".join(config.OLLAMA_FALLBACK_MODELS),
        "Cycle Interval (s)":   config.CYCLE_INTERVAL_SEC,
        "Circuit Breaker Limit": config.CIRCUIT_BREAKER_LIMIT,
        "Max Workers":          config.MAX_CONCURRENT_WORKERS,
        "Projects Dir":         str(config.PROJECTS_DIR),
        "ChromaDB Path":        config.CHROMA_PATH,
        "Monetization Enabled": config.MONETIZATION_ENABLED,
    }
    for k, v in cfg_data.items():
        st.text_input(k, value=str(v), disabled=True)

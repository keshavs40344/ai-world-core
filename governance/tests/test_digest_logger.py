"""
governance/tests/test_digest_logger.py
=======================================
Unit tests for DigestLogger.
"""
import json
import pytest
from pathlib import Path

import genesis.config as _config
from genesis.state_db import init_db


@pytest.fixture(autouse=True)
def isolated_paths(tmp_path, monkeypatch):
    logs = tmp_path / "logs"
    logs.mkdir()
    db = tmp_path / "state.db"
    monkeypatch.setattr(_config, "LOGS_DIR", logs)
    monkeypatch.setattr(_config, "DIGEST_LOG_PATH", logs / "daily_digest.jsonl")
    monkeypatch.setattr(_config, "STATE_DB_PATH", db)
    import genesis.state_db as sdb
    import importlib; importlib.reload(sdb)
    sdb.init_db()


def test_record_tier_a():
    from governance.digest_logger import DigestLogger
    dl = DigestLogger()
    manifest = {
        "project_id": "abc-123",
        "name": "my_tool",
        "category": "Dev Tools",
        "subcategory": "CLI",
        "description": "A test tool",
    }
    dl.record_tier_a(manifest)

    entries = _config.DIGEST_LOG_PATH.read_text().strip().split("\n")
    assert len(entries) == 1
    data = json.loads(entries[0])
    assert data["project_name"] == "my_tool"
    assert data["tier"] == "A"


def test_generate_daily_summary():
    from governance.digest_logger import DigestLogger
    dl = DigestLogger()
    summary = dl.generate_daily_summary()
    assert "Genesis Daily Digest" in summary
    assert "Tier A Commits" in summary


def test_summary_file_written():
    from governance.digest_logger import DigestLogger
    from datetime import datetime, timezone
    dl = DigestLogger()
    dl.generate_daily_summary()
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out = _config.LOGS_DIR / f"digest_{date_str}.md"
    assert out.exists()

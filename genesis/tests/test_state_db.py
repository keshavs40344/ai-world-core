"""
genesis/tests/test_state_db.py
==============================
Unit tests for the SQLite state store.
"""

import pytest
from pathlib import Path
import tempfile
import os

# Redirect DB to a temp file during tests
import genesis.config as _config

@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    """Use a fresh temp database for every test."""
    db = tmp_path / "test_state.db"
    monkeypatch.setattr(_config, "STATE_DB_PATH", db)
    from genesis import state_db as sdb
    sdb.init_db()
    yield sdb


def test_enqueue_and_claim(isolated_db):
    sdb = isolated_db
    task_id = sdb.enqueue_task("my_project", {"key": "value"}, priority=3)
    assert task_id

    task = sdb.claim_next_task()
    assert task is not None
    assert task["project_name"] == "my_project"
    assert task["status"] == "IN_PROGRESS"
    assert task["payload"] == {"key": "value"}


def test_claim_returns_none_on_empty_queue(isolated_db):
    sdb = isolated_db
    assert sdb.claim_next_task() is None


def test_update_task_status(isolated_db):
    sdb = isolated_db
    task_id = sdb.enqueue_task("proj", {})
    sdb.update_task_status(task_id, "PASSED", increment_attempts=True)
    task = sdb.get_task(task_id)
    assert task["status"] == "PASSED"
    assert task["attempts"] == 1


def test_priority_ordering(isolated_db):
    sdb = isolated_db
    sdb.enqueue_task("low_priority", {}, priority=9)
    sdb.enqueue_task("high_priority", {}, priority=1)
    task = sdb.claim_next_task()
    assert task["project_name"] == "high_priority"


def test_cycle_tracking(isolated_db):
    sdb = isolated_db
    cycle_id = sdb.start_cycle()
    assert cycle_id
    sdb.finish_cycle(cycle_id, outcome="SUCCESS", tasks_run=3, tasks_passed=3)


def test_log_event(isolated_db):
    sdb = isolated_db
    sdb.log_event("test event", level="INFO", category="TEST", payload={"x": 1})
    events = sdb.get_recent_events(hours=1)
    assert len(events) >= 1
    assert events[0]["message"] == "test event"
    assert events[0]["payload"] == {"x": 1}

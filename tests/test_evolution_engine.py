"""
tests/test_evolution_engine.py
==============================
Automated unit and integration test suite for the Project Genesis Self-Evolution Engine:
  - Feedback Store & Anti-pattern retrieval
  - Failure Taxonomy Classifier
  - Prompt Registry & Auto-Promotion
  - Dynamic Self-Tuning Config
  - Meta-RADAR Category Multiplier
"""

import os
import tempfile
import pytest
from pathlib import Path

from genesis import config
from foundry.feedback_store import (
    record_feedback,
    get_failure_patterns_for_category,
    get_category_performance_stats,
)
from foundry.failure_classifier import (
    classify_failure,
    CATEGORY_ASYNC_MISUSE,
    CATEGORY_IMPORT_DEPENDENCY,
    CATEGORY_RUFF_VIOLATION,
    CATEGORY_TEST_ASSERTION,
)
from foundry.prompt_registry import (
    register_prompt,
    record_prompt_outcome,
    get_active_prompt,
    auto_promote_best_version,
)
from genesis.dynamic_config import DynamicConfigManager


def test_failure_classifier_heuristics():
    # 1. Async error
    async_log = "RuntimeError: Task <Task> got Future attached to a different loop. coroutine was never awaited"
    res1 = classify_failure(async_log)
    assert res1.category == CATEGORY_ASYNC_MISUSE

    # 2. Import error
    import_log = "ModuleNotFoundError: No module named 'fastapi_toolkit'"
    res2 = classify_failure(import_log)
    assert res2.category == CATEGORY_IMPORT_DEPENDENCY
    assert "fastapi_toolkit" in res2.summary

    # 3. Ruff linter violation
    ruff_log = "src/main.py:12:1: F401 `os` imported but unused\nFound 1 error."
    res3 = classify_failure(ruff_log)
    assert res3.category == CATEGORY_RUFF_VIOLATION
    assert "F401" in res3.ruff_rules

    # 4. Pytest assertion failure
    assert_log = "AssertionError: assert calculate_total(10) == 20"
    res4 = classify_failure(assert_log)
    assert res4.category == CATEGORY_TEST_ASSERTION


def test_feedback_store_and_pattern_injection(tmp_path, monkeypatch):
    # Route db to temporary file
    db_file = tmp_path / "test_state.db"
    monkeypatch.setattr(config, "STATE_DB_PATH", db_file)

    # Record some synthetic failures
    record_feedback(
        project_name="proj_alpha",
        category="data_pipeline",
        tier="TIER_A",
        status="FAIL",
        failure_type="IMPORT_DEPENDENCY_ERROR",
        error_summary="Missing pandas dependency in requirements.txt",
    )
    record_feedback(
        project_name="proj_beta",
        category="data_pipeline",
        tier="TIER_A",
        status="FAIL",
        failure_type="ASYNC_MISUSE",
        error_summary="Unawaited coroutine in batch processor",
    )
    record_feedback(
        project_name="proj_gamma",
        category="data_pipeline",
        tier="TIER_A",
        status="PASS",
    )

    # Query patterns
    patterns = get_failure_patterns_for_category("data_pipeline")
    assert len(patterns) >= 2
    assert any("IMPORT_DEPENDENCY_ERROR" in p for p in patterns)
    assert any("ASYNC_MISUSE" in p for p in patterns)

    # Verify performance stats
    stats = get_category_performance_stats()
    assert "data_pipeline" in stats
    assert stats["data_pipeline"]["total_runs"] == 3
    assert stats["data_pipeline"]["passes"] == 1
    assert stats["data_pipeline"]["failures"] == 2


def test_prompt_registry_and_auto_promotion(tmp_path, monkeypatch):
    db_file = tmp_path / "test_prompt.db"
    monkeypatch.setattr(config, "STATE_DB_PATH", db_file)

    # Initial default prompt should exist
    default_prompt = get_active_prompt("core_engineer", "developer_tools")
    assert default_prompt.version_tag.startswith("v1.0.0")

    # Register candidate v2.0
    v2_id = register_prompt(
        role="core_engineer",
        template_text="Custom prompt v2 {manifest_json}",
        version_tag="v2.0.0-experimental",
        category="developer_tools",
    )

    # Log 5 successful runs for v2
    for _ in range(5):
        record_prompt_outcome(v2_id, passed_first_try=True, retries=0, tier_b_approved=True)

    # Trigger auto-promotion
    promoted = auto_promote_best_version("core_engineer", "developer_tools", min_sample=3)
    assert promoted == "v2.0.0-experimental"

    # Now get_active_prompt should return v2.0.0-experimental
    active = get_active_prompt("core_engineer", "developer_tools")
    assert active.version_tag == "v2.0.0-experimental"


def test_dynamic_self_tuning_config(tmp_path, monkeypatch):
    db_file = tmp_path / "test_tuning.db"
    monkeypatch.setattr(config, "STATE_DB_PATH", db_file)

    # With no runs, default config returned
    manager = DynamicConfigManager()
    tuned = manager.tune()
    assert tuned.circuit_breaker_limit in [3, 4, 5, 6, 7]
    assert tuned.max_concurrent_workers >= 1

    # Simulate 5 consecutive failures
    for i in range(5):
        record_feedback(
            project_name=f"failing_{i}",
            category="general",
            tier="TIER_A",
            status="FAIL",
            failure_type="PYTEST_ASSERT",
            error_summary="Test failed",
        )

    # Low pass rate should raise circuit breaker limit to give more retry headroom
    tuned_after_failures = manager.tune()
    assert tuned_after_failures.circuit_breaker_limit >= config.CIRCUIT_BREAKER_LIMIT

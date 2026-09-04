"""
radar/tests/test_manifest_writer.py
=====================================
Unit tests for ManifestWriter.
"""

import json
import pytest
from pathlib import Path

import genesis.config as _config


@pytest.fixture(autouse=True)
def isolated_paths(tmp_path, monkeypatch):
    manifests = tmp_path / "manifests"
    manifests.mkdir()
    monkeypatch.setattr(_config, "MANIFESTS_DIR", manifests)
    monkeypatch.setattr(_config, "MANIFEST_PATH", manifests / "project_manifest.json")


def test_dry_run_manifest_writes_file():
    from radar.manifest_writer import ManifestWriter
    manifest = ManifestWriter.dry_run_manifest()

    assert manifest["name"] == "csv_to_json_cli"
    assert manifest["schema_version"] == "1.0"
    assert "project_id" in manifest
    assert len(manifest["goals"]) >= 3

    # Verify file was written
    assert _config.MANIFEST_PATH.exists()
    loaded = json.loads(_config.MANIFEST_PATH.read_text())
    assert loaded["name"] == manifest["name"]


def test_write_top():
    from radar.manifest_writer import ManifestWriter
    from radar.gap_auditor import Opportunity

    opp = Opportunity(
        name="test_tool",
        category="Dev Tools",
        subcategory="CLI",
        description="A test tool",
        rationale="Testing",
        goals=["goal 1"],
        priority_score=0.9,
    )
    mw = ManifestWriter()
    manifest = mw.write_top([opp])

    assert manifest["name"] == "test_tool"
    assert manifest["category"] == "Dev Tools"
    assert _config.MANIFEST_PATH.exists()


def test_write_top_raises_on_empty():
    from radar.manifest_writer import ManifestWriter
    with pytest.raises(ValueError, match="no opportunities"):
        ManifestWriter().write_top([])


def test_load_returns_none_when_absent():
    from radar.manifest_writer import ManifestWriter
    assert ManifestWriter.load() is None


def test_load_returns_manifest():
    from radar.manifest_writer import ManifestWriter
    ManifestWriter.dry_run_manifest()
    manifest = ManifestWriter.load()
    assert manifest is not None
    assert manifest["name"] == "csv_to_json_cli"

"""
radar/manifest_writer.py
========================
RADAR Controller — Step 3: Project Manifest Generation.

Takes the top-ranked Opportunity from GapAuditor and serialises it into
`project_manifest.json` — the canonical input contract for FOUNDRY.

Also provides `dry_run_manifest()` for smoke-testing the pipeline
without Ollama or network access.
"""

from __future__ import annotations

import json
import uuid
import logging
from datetime import datetime, timezone
from typing import Any

from genesis import config
from radar.gap_auditor import Opportunity

log = logging.getLogger("radar.manifest")


# ---------------------------------------------------------------------------
# Manifest schema
# ---------------------------------------------------------------------------

def _build_manifest(opportunity: Opportunity) -> dict[str, Any]:
    """Convert an Opportunity into a structured project_manifest dict."""
    return {
        "schema_version": "1.0",
        "project_id": str(uuid.uuid4()),
        "name": opportunity.name,
        "category": opportunity.category,
        "subcategory": opportunity.subcategory,
        "description": opportunity.description,
        "rationale": opportunity.rationale,
        "goals": opportunity.goals,
        "estimated_complexity": opportunity.estimated_complexity,
        "priority_score": opportunity.priority_score,
        "source_signals": opportunity.source_signals,

        # FOUNDRY contracts — filled in by FOUNDRY or left as defaults
        "io_schema": {
            "inputs":  [],
            "outputs": [],
        },
        "benchmarks": {
            "max_latency_ms":     None,
            "max_memory_mb":      None,
            "min_throughput_rps": None,
        },
        "test_criteria": [
            "All unit tests must pass (pytest exit 0)",
            "Lint must pass (ruff exit 0)",
            "No hardcoded secrets or credentials in source",
            "README.md must be present",
        ],
        "license": "MIT",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "PENDING",
    }


# ---------------------------------------------------------------------------
# Writer class
# ---------------------------------------------------------------------------

class ManifestWriter:
    """
    Serialises the highest-priority Opportunity to `project_manifest.json`.
    Also stores a timestamped archive copy for historical reference.
    """

    def write_top(self, opportunities: list[Opportunity]) -> dict[str, Any]:
        """
        Write the top opportunity to the canonical manifest path.
        Returns the manifest dict.
        Raises ValueError if the opportunities list is empty.
        """
        if not opportunities:
            raise ValueError("ManifestWriter.write_top: no opportunities provided.")

        top = opportunities[0]
        manifest = _build_manifest(top)

        # Write canonical manifest
        config.MANIFEST_PATH.write_text(
            json.dumps(manifest, indent=2), encoding="utf-8"
        )
        log.info(f"[ManifestWriter] Manifest written: {config.MANIFEST_PATH}")

        # Archive copy (never overwritten, useful for audit trail)
        archive_path = config.MANIFESTS_DIR / f"{manifest['project_id']}.json"
        archive_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        log.info(f"[ManifestWriter] Archived: {archive_path.name}")

        return manifest

    @staticmethod
    def dry_run_manifest() -> dict[str, Any]:
        """
        Return a synthetic manifest for dry-run / smoke-test mode.
        No LLM or network calls are made.
        """
        opp = Opportunity(
            name="csv_to_json_cli",
            category="Developer Tools",
            subcategory="Data Conversion",
            description="A zero-dependency CLI tool that converts CSV files to JSON with type inference.",
            rationale="Existing tools require heavy dependencies or lack streaming support for large files.",
            goals=[
                "Accept CSV via stdin or file path",
                "Auto-infer column types (int, float, bool, string, date)",
                "Output newline-delimited JSON (NDJSON) or pretty-printed JSON",
                "Stream large files without loading all into memory",
                "100% stdlib Python — no pip install required",
            ],
            estimated_complexity="low",
            priority_score=0.85,
            source_signals=["pycsv", "pandas", "csvkit"],
        )
        manifest = _build_manifest(opp)

        # Write to canonical path so downstream pipeline can read it
        config.MANIFEST_PATH.write_text(
            json.dumps(manifest, indent=2), encoding="utf-8"
        )
        log.info(f"[ManifestWriter] Dry-run manifest written: {manifest['name']}")
        return manifest

    @staticmethod
    def load() -> dict[str, Any] | None:
        """Load and return the current canonical manifest, or None if absent."""
        if not config.MANIFEST_PATH.exists():
            return None
        try:
            return json.loads(config.MANIFEST_PATH.read_text(encoding="utf-8"))
        except Exception as exc:
            log.error(f"Failed to load manifest: {exc}")
            return None

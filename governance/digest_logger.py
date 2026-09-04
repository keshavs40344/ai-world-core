"""
governance/digest_logger.py
============================
Tier A — Silent daily digest logger.

Appends structured JSON entries to `logs/daily_digest.jsonl` for every
Tier A auto-commit. Generates a human-readable Markdown digest summary
at the end of each day (called by the scheduler at midnight).
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

from genesis import config
from genesis.state_db import get_recent_events

log = logging.getLogger("governance.digest")


class DigestLogger:
    """
    Records Tier A events and generates periodic human-readable summaries.
    """

    def record_tier_a(self, manifest: dict[str, Any]) -> None:
        """Append a Tier A commit entry to the daily digest log."""
        entry = {
            "timestamp":    datetime.now(timezone.utc).isoformat(),
            "tier":         "A",
            "event":        "AUTO_COMMIT",
            "project_id":   manifest.get("project_id"),
            "project_name": manifest.get("name"),
            "category":     f"{manifest.get('category')} -> {manifest.get('subcategory')}",
            "description":  manifest.get("description", ""),
        }
        try:
            with open(config.DIGEST_LOG_PATH, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
            log.debug(f"[Digest] Logged Tier A commit: {manifest.get('name')}")
        except Exception as exc:
            log.warning(f"[Digest] Failed to write digest entry: {exc}")

    def generate_daily_summary(self) -> str:
        """
        Generate a Markdown summary of the last 24 hours of activity.
        Writes to `logs/digest_YYYYMMDD.md` and returns the content.
        """
        events = get_recent_events(hours=24.0, limit=500)

        # Group by category
        by_category: dict[str, int] = {}
        tier_a_count = tier_b_count = error_count = 0

        for e in events:
            cat = e.get("category", "OTHER")
            by_category[cat] = by_category.get(cat, 0) + 1
            level = e.get("level", "INFO")
            if level == "ERROR":
                error_count += 1

        # Count from jsonl
        tier_a_entries = self._load_recent_tier_a()
        tier_a_count = len(tier_a_entries)

        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        summary = self._format_summary(date_str, tier_a_entries, events, by_category, error_count)

        out_path = config.LOGS_DIR / f"digest_{date_str}.md"
        out_path.write_text(summary, encoding="utf-8")
        log.info(f"[Digest] Daily summary written: {out_path.name}")
        return summary

    def _load_recent_tier_a(self) -> list[dict]:
        """Load Tier A entries from the last 24 hours."""
        if not config.DIGEST_LOG_PATH.exists():
            return []
        from datetime import timedelta
        cutoff = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
        entries = []
        try:
            with open(config.DIGEST_LOG_PATH, encoding="utf-8") as f:
                for line in f:
                    try:
                        e = json.loads(line.strip())
                        if e.get("timestamp", "") >= cutoff:
                            entries.append(e)
                    except Exception:
                        pass
        except Exception:
            pass
        return entries

    @staticmethod
    def _format_summary(
        date_str: str,
        tier_a: list[dict],
        db_events: list[dict],
        by_category: dict[str, int],
        error_count: int,
    ) -> str:
        tier_a_rows = "\n".join(
            f"| {e.get('project_name', '?')} | {e.get('category', '?')} | {e.get('timestamp', '?')[:19]} |"
            for e in tier_a
        ) or "| — | — | — |"

        cat_rows = "\n".join(
            f"| {cat} | {cnt} |"
            for cat, cnt in sorted(by_category.items(), key=lambda x: -x[1])
        ) or "| — | 0 |"

        return f"""\
# 🧬 Genesis Daily Digest — {date_str}

## Summary

| Metric | Count |
|---|---|
| Tier A Auto-Commits | {len(tier_a)} |
| Total Events | {len(db_events)} |
| Errors | {error_count} |

## Tier A Commits

| Project | Category | Time (UTC) |
|---|---|---|
{tier_a_rows}

## Event Activity by Category

| Category | Events |
|---|---|
{cat_rows}

---
*Generated automatically by Project Genesis — Digest Logger*
"""

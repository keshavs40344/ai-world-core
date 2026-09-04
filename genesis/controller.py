"""
genesis/controller.py
=====================
Genesis-Controller — the main orchestration event loop.

Responsibilities:
  1. Initialise all subsystems (DB, ChromaDB, Docker image).
  2. Kick off the APScheduler background loop:
       RADAR scan → FOUNDRY build → VAULT commit → GOVERNANCE gate
  3. Handle graceful shutdown (SIGINT / SIGTERM).
  4. Monitor RAM and switch to fallback LLM models when needed.
  5. Provide a --dry-run CLI flag for smoke-testing without LLM calls.

Usage:
    python -m genesis.controller           # start the live engine
    python -m genesis.controller --dry-run # smoke-test, no LLM calls
"""

from __future__ import annotations

import argparse
import logging
import signal
import sys
import time
from datetime import datetime, timezone

# ── Windows UTF-8 fix ──────────────────────────────────────────────────────
# PowerShell / cmd.exe default to cp1252 which can't encode Rich's Unicode
# box-drawing and emoji characters. Force UTF-8 for stdout/stderr.
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
# ──────────────────────────────────────────────────────────────────────────

import psutil
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from rich.console import Console
from rich.logging import RichHandler

# Genesis internals
from genesis import config
from genesis.state_db import init_db, start_cycle, finish_cycle, log_event

console = Console()

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=console, rich_tracebacks=True)],
)
log = logging.getLogger("genesis")


# ---------------------------------------------------------------------------
# Hardware probe
# ---------------------------------------------------------------------------

def _available_ram_gb() -> float:
    return psutil.virtual_memory().available / (1024 ** 3)


def _active_model() -> str:
    ram = _available_ram_gb()
    model = config.get_active_model(ram)
    if model != config.OLLAMA_PRIMARY_MODEL:
        log.warning(
            f"Low RAM ({ram:.1f} GB available) — falling back to model: {model}"
        )
    return model


# ---------------------------------------------------------------------------
# Subsystem initialisation
# ---------------------------------------------------------------------------

def _init_subsystems(dry_run: bool) -> None:
    """Boot all persistent services required before the main loop starts."""
    log.info("[bold green]▶ Initialising Project Genesis[/bold green]",
             extra={"markup": True})

    # 1. Database
    log.info("  ◆ Bootstrapping SQLite state DB …")
    init_db()
    log_event("Genesis controller starting", category="GENESIS",
              payload={"dry_run": dry_run,
                       "version": "1.0.0",
                       "started_at": datetime.now(timezone.utc).isoformat()})

    # 2. Vault vector store
    log.info("  ◆ Connecting to ChromaDB vault …")
    try:
        from vault.vector_store import VectorStore
        VectorStore()   # initialises collections
        log.info("    ChromaDB OK")
    except Exception as exc:
        log.warning(f"    ChromaDB unavailable ({exc}) — semantic vault disabled.")

    # 3. Docker worker image
    if not dry_run:
        log.info("  ◆ Verifying Docker worker image …")
        try:
            from foundry.sandbox_runner import SandboxRunner
            SandboxRunner.ensure_worker_image()
            log.info("    Docker worker image OK")
        except Exception as exc:
            log.warning(f"    Docker unavailable ({exc}) — sandboxing disabled.")

    log.info("[bold green]▶ Subsystems ready.[/bold green]",
             extra={"markup": True})


# ---------------------------------------------------------------------------
# Cycle execution
# ---------------------------------------------------------------------------

def _run_cycle(dry_run: bool) -> None:
    """Single execution of the full RADAR → FOUNDRY → VAULT → GOVERNANCE pipeline."""
    cycle_id = start_cycle()
    tasks_run = tasks_passed = 0
    outcome = "SUCCESS"

    try:
        log.info(f"[cyan]━━━ Cycle {cycle_id[:8]} started ━━━[/cyan]",
                 extra={"markup": True})

        # ── STEP 1: RADAR ──────────────────────────────────────────────────
        log.info("  [STEP 1] RADAR: scanning for opportunities …")
        if not dry_run:
            from radar.scanner import RadarScanner
            from radar.gap_auditor import GapAuditor
            from radar.manifest_writer import ManifestWriter

            model = _active_model()
            scanner = RadarScanner()
            raw_trends = scanner.scan()

            auditor = GapAuditor(model=model)
            opportunities = auditor.analyse(raw_trends)

            writer = ManifestWriter()
            manifest = writer.write_top(opportunities)
            log.info(f"    Manifest written: {manifest['name']}")
        else:
            # Dry-run: use a synthetic manifest
            from radar.manifest_writer import ManifestWriter
            manifest = ManifestWriter.dry_run_manifest()
            log.info(f"    [DRY-RUN] Synthetic manifest: {manifest['name']}")

        # ── STEP 2: FOUNDRY ────────────────────────────────────────────────
        log.info("  [STEP 2] FOUNDRY: provisioning worker agents …")
        if not dry_run:
            from foundry.agent_factory import AgentFactory
            from foundry.taxonomy_engine import TaxonomyEngine
            from foundry.test_loop import TestLoop

            taxonomy = TaxonomyEngine()
            namespace = taxonomy.classify(manifest)
            log.info(f"    Classified as: {namespace}")

            factory = AgentFactory(model=_active_model())
            project_dir = factory.generate(manifest, namespace)

            loop = TestLoop(project_dir=project_dir)
            result = loop.run(task_payload=manifest)
            tasks_run += 1
            if result["status"] == "PASSED":
                tasks_passed += 1
        else:
            log.info("    [DRY-RUN] Skipping code generation and sandbox.")

        # ── STEP 3: VAULT ──────────────────────────────────────────────────
        if not dry_run and tasks_passed > 0:
            log.info("  [STEP 3] VAULT: committing validated artifacts …")
            from vault.git_manager import GitManager
            gm = GitManager()
            gm.commit_project(manifest["project_id"], manifest["name"])
            log.info("    Git commit OK")

            from vault.vector_store import VectorStore
            vs = VectorStore()
            vs.index_project(manifest)
            log.info("    Vector index updated")

        # ── STEP 4: GOVERNANCE ─────────────────────────────────────────────
        if not dry_run and tasks_passed > 0:
            log.info("  [STEP 4] GOVERNANCE: evaluating release tier …")
            from governance.tier_a_validator import TierAValidator
            from governance.tier_b_gate import TierBGate
            from governance.digest_logger import DigestLogger

            validator = TierAValidator()
            tier_a_ok = validator.validate(manifest)

            if tier_a_ok:
                logger = DigestLogger()
                logger.record_tier_a(manifest)
                log.info("    Tier A: auto-committed to vault ✓")
            else:
                gate = TierBGate()
                gate.freeze_and_notify(manifest)
                log.info("    Tier B: release card issued, execution frozen.")

    except Exception as exc:
        outcome = "FAILED"
        log.exception(f"Cycle {cycle_id[:8]} encountered an unhandled error: {exc}")
        log_event(str(exc), level="ERROR", category="GENESIS",
                  payload={"cycle_id": cycle_id})
    finally:
        finish_cycle(cycle_id, outcome=outcome,
                     tasks_run=tasks_run, tasks_passed=tasks_passed)
        log.info(
            f"[cyan]━━━ Cycle {cycle_id[:8]} finished: {outcome} "
            f"({tasks_passed}/{tasks_run} tasks) ━━━[/cyan]",
            extra={"markup": True},
        )


# ---------------------------------------------------------------------------
# Scheduler / main entry point
# ---------------------------------------------------------------------------

def _build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="genesis",
        description="Genesis-Controller — Autonomous Local-First Software Foundry",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Run one cycle with synthetic data; no LLM calls or Docker containers.",
    )
    p.add_argument(
        "--once",
        action="store_true",
        help="Run a single cycle then exit (useful for cron-driven invocation).",
    )
    p.add_argument(
        "--interval",
        type=int,
        default=config.CYCLE_INTERVAL_SEC,
        help=f"Seconds between cycles (default: {config.CYCLE_INTERVAL_SEC}).",
    )
    return p


def main() -> None:
    args = _build_arg_parser().parse_args()

    _init_subsystems(dry_run=args.dry_run)

    if args.once or args.dry_run:
        # Single-shot execution
        _run_cycle(dry_run=args.dry_run)
        return

    # Continuous background scheduler
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(
        func=_run_cycle,
        trigger=IntervalTrigger(seconds=args.interval),
        kwargs={"dry_run": False},
        id="genesis_cycle",
        replace_existing=True,
        max_instances=1,          # Never run two cycles simultaneously
        coalesce=True,
    )
    scheduler.start()

    log.info(
        f"[bold green]✔ Genesis engine running (cycle every {args.interval}s). "
        "Press Ctrl+C to stop.[/bold green]",
        extra={"markup": True},
    )

    # Run the first cycle immediately without waiting for the interval
    _run_cycle(dry_run=False)

    # Graceful shutdown on SIGINT / SIGTERM
    def _shutdown(sig, frame):          # noqa: ANN001
        log.info("Shutdown signal received — stopping scheduler …")
        scheduler.shutdown(wait=False)
        log_event("Genesis controller stopped", category="GENESIS")
        sys.exit(0)

    signal.signal(signal.SIGINT,  _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    # Keep main thread alive
    while True:
        time.sleep(5)


if __name__ == "__main__":
    main()

"""
governance/tier_a_validator.py
===============================
Tier A — Automated internal validation (linting + unit tests).

Runs the full quality gate inside the Docker sandbox:
  1. `ruff check . --fix`   — lint & auto-fix
  2. `pytest --tb=short -q` — unit tests

Both must exit with code 0 for Tier A consensus to pass.
On success, the project is eligible for automatic vault commit.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from genesis import config
from foundry.sandbox_runner import SandboxRunner

log = logging.getLogger("governance.tier_a")

import platform

if platform.system() == "Windows":
    _VALIDATE_COMMAND = (
        "python -m pip install -q -r requirements.txt "
        "&& ruff check . --fix --quiet "
        "&& pytest --tb=short -q --no-header"
    )
else:
    _VALIDATE_COMMAND = (
        "pip install -q -r requirements.txt 2>&1 "
        "&& ruff check . --fix --quiet 2>&1 "
        "&& pytest --tb=short -q --no-header 2>&1"
    )


class TierAValidator:
    """
    Runs automated linting + test validation inside the Docker sandbox.
    Returns True if both pass (Tier A consensus), False otherwise.
    """

    def __init__(self) -> None:
        self.sandbox = SandboxRunner()

    def validate(self, manifest: dict[str, Any]) -> bool:
        """
        Validate the generated project for the given manifest.
        Returns True on full pass, False on any failure.
        """
        project_name = manifest.get("name", "unknown")
        project_dir = config.PROJECTS_DIR / project_name

        if not project_dir.exists():
            log.error(f"[TierA] Project directory not found: {project_dir}")
            return False

        log.info(f"[TierA] Validating '{project_name}' …")
        result = self.sandbox.run(
            project_dir=project_dir,
            command=_VALIDATE_COMMAND,
        )

        if result.success:
            log.info(f"[TierA] ✅ '{project_name}' passed lint + tests.")
            return True
        else:
            log.warning(
                f"[TierA] ❌ '{project_name}' failed validation "
                f"(exit {result.exit_code}).\n"
                f"{result.stdout[-1000:]}"
            )
            return False

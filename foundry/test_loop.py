"""
foundry/test_loop.py
====================
FOUNDRY — Self-healing test iteration engine (Circuit Breaker pattern).

Algorithm:
  1. Run `pip install -r requirements.txt && ruff check . && pytest` inside
     the Docker sandbox.
  2. If tests pass → mark task PASSED, return success result.
  3. If tests fail:
     a. Parse the error output.
     b. Prompt the LLM to generate a targeted patch (diff / file overwrites).
     c. Apply the patch to the project directory.
     d. Increment attempt counter and retry.
  4. After `config.CIRCUIT_BREAKER_LIMIT` consecutive failures:
     a. Archive the failure context to the ChromaDB vault.
     b. Mark task as CIRCUIT_BROKEN.
     c. Return a failure result.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests

from genesis import config
from genesis.state_db import update_task_status, log_event
from foundry.sandbox_runner import SandboxRunner, RunResult

log = logging.getLogger("foundry.testloop")

import platform

if platform.system() == "Windows":
    _TEST_COMMAND = (
        "python -m pip install -q -r requirements.txt "
        "&& ruff check . --fix --quiet "
        "&& pytest --tb=short -q"
    )
else:
    _TEST_COMMAND = (
        "pip install -q -r requirements.txt 2>&1 "
        "&& ruff check . --fix --quiet 2>&1 "
        "&& pytest --tb=short -q 2>&1"
    )

_PATCH_SYSTEM_PROMPT = """\
You are an expert Python debugging assistant for an autonomous software foundry.
A test run inside a Docker container has failed. Analyse the error output and
return patches to fix the failing tests and any runtime errors.

Rules:
- Only fix bugs — do not refactor or add features
- Return a JSON object where each key is a file path and value is the COMPLETE
  corrected content of that file (not a diff — the full file)
- Only include files that need to change
- Return ONLY the JSON — no prose, no markdown
"""


@dataclass
class LoopResult:
    status: str          # "PASSED" | "CIRCUIT_BROKEN" | "FAILED"
    attempts: int
    final_output: str
    project_dir: str


class TestLoop:
    """
    Runs the test pipeline in a loop, applying LLM patches on each failure,
    until tests pass or the circuit breaker limit is reached.
    """

    def __init__(self, project_dir: Path, model: str = "") -> None:
        self.project_dir = project_dir
        self.model = model or config.OLLAMA_PRIMARY_MODEL
        self.sandbox = SandboxRunner()

    def run(self, task_payload: dict[str, Any]) -> dict[str, Any]:
        """
        Execute the self-healing test loop.
        Returns a dict compatible with LoopResult for use by the controller.
        """
        task_id = task_payload.get("project_id", "unknown")
        max_attempts = config.CIRCUIT_BREAKER_LIMIT
        last_output = ""

        for attempt in range(1, max_attempts + 1):
            log.info(f"[TestLoop] Attempt {attempt}/{max_attempts} for '{task_payload['name']}'")
            self._sanitize_requirements(self.project_dir)

            result: RunResult = self.sandbox.run(
                project_dir=self.project_dir,
                command=_TEST_COMMAND,
            )
            last_output = result.stdout + "\n" + result.stderr

            if result.success:
                log.info(f"[TestLoop] ✅ Tests passed on attempt {attempt}.")
                update_task_status(task_id, "PASSED", increment_attempts=True)
                log_event(
                    f"Tests passed: {task_payload['name']}",
                    category="FOUNDRY",
                    payload={"attempt": attempt, "project_id": task_id},
                )
                return LoopResult(
                    status="PASSED",
                    attempts=attempt,
                    final_output=last_output,
                    project_dir=str(self.project_dir),
                ).__dict__

            # Tests failed — try LLM patch
            log.warning(
                f"[TestLoop] ❌ Attempt {attempt} failed (exit {result.exit_code}). "
                "Requesting LLM patch …"
            )
            update_task_status(
                task_id, "IN_PROGRESS",
                error_log=last_output[:2000],
                increment_attempts=True,
            )

            if attempt < max_attempts:
                patched = self._apply_llm_patch(task_payload, last_output)
                if not patched:
                    log.warning("[TestLoop] No patch generated — retrying unchanged.")

        # Circuit breaker triggered
        log.error(
            f"[TestLoop] 💥 Circuit breaker triggered for '{task_payload['name']}' "
            f"after {max_attempts} attempts."
        )
        self._archive_failure(task_payload, last_output)
        update_task_status(task_id, "CIRCUIT_BROKEN", error_log=last_output[:4000])
        log_event(
            f"Circuit broken: {task_payload['name']}",
            level="ERROR",
            category="FOUNDRY",
            payload={"attempts": max_attempts, "project_id": task_id},
        )
        return LoopResult(
            status="CIRCUIT_BROKEN",
            attempts=max_attempts,
            final_output=last_output,
            project_dir=str(self.project_dir),
        ).__dict__

    @staticmethod
    def _sanitize_requirements(project_dir: Path) -> None:
        """Strip trailing commas, invalid characters, and empty lines from requirements.txt."""
        req_path = project_dir / "requirements.txt"
        if not req_path.exists():
            return
        try:
            cleaned_lines = []
            for line in req_path.read_text(encoding="utf-8").splitlines():
                cleaned = line.strip().rstrip(",")
                if cleaned and not cleaned.startswith("#"):
                    cleaned_lines.append(cleaned)
            req_path.write_text("\n".join(cleaned_lines) + "\n", encoding="utf-8")
        except Exception:
            pass

    # -----------------------------------------------------------------------
    # LLM patch generation
    # -----------------------------------------------------------------------

    def _apply_llm_patch(
        self, manifest: dict[str, Any], error_output: str
    ) -> bool:
        """
        Ask Ollama to generate file patches based on the error output.
        Applies the patches to the project directory.
        Returns True if at least one file was patched.
        """
        # Summarise project source for context
        source_ctx = self._summarise_source(max_chars=6000)

        user_prompt = (
            f"PROJECT: {manifest['name']}\n"
            f"DESCRIPTION: {manifest['description']}\n\n"
            f"CURRENT SOURCE:\n{source_ctx}\n\n"
            f"ERROR OUTPUT:\n{error_output[:3000]}\n\n"
            "Generate patches to fix all errors. Return a JSON object mapping "
            "file paths to their corrected complete content."
        )

        raw = ""
        try:
            resp = requests.post(
                f"{config.OLLAMA_HOST}/api/chat",
                headers=config.OLLAMA_HEADERS,
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": _PATCH_SYSTEM_PROMPT},
                        {"role": "user",   "content": user_prompt},
                    ],
                    "stream": False,
                    "format": "json",
                    "options": {
                        "temperature": 0.1,
                        "num_ctx": config.OLLAMA_CTX_WINDOW,
                        "num_predict": 1024,
                    },
                },
                timeout=120,
            )
            resp.raise_for_status()
            raw = resp.json()["message"]["content"]
        except Exception as exc:
            log.warning(f"[Patch] Remote patch generation failed ({exc}) — falling back to local llama3.2:1b …")
            try:
                resp = requests.post(
                    "http://127.0.0.1:11434/api/chat",
                    json={
                        "model": "llama3.2:1b",
                        "messages": [
                            {"role": "system", "content": _PATCH_SYSTEM_PROMPT},
                            {"role": "user",   "content": user_prompt},
                        ],
                        "stream": False,
                        "format": "json",
                        "options": {
                            "temperature": 0.1,
                            "num_ctx": 4096,
                            "num_predict": 1024,
                        },
                    },
                    timeout=120,
                )
                resp.raise_for_status()
                raw = resp.json()["message"]["content"]
            except Exception as local_exc:
                log.error(f"[Patch] Local patch fallback also failed: {local_exc}")
                return False

        try:
            patches = self._parse_patches(raw)
            if not patches:
                return False

            for rel_path, content in patches.items():
                safe = self.project_dir / rel_path.lstrip("/\\")
                safe.parent.mkdir(parents=True, exist_ok=True)
                safe.write_text(content, encoding="utf-8")
                log.debug(f"  Patched: {rel_path}")

            log.info(f"  [Patch] {len(patches)} file(s) patched.")
            return True

        except Exception as exc:
            log.error(f"[Patch] Failed applying patches: {exc}")
            return False

    @staticmethod
    def _parse_patches(raw: str) -> dict[str, str]:
        cleaned = raw.strip()
        cleaned = re.sub(r"^```[a-z]*\n?", "", cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r"\n?```$", "", cleaned, flags=re.MULTILINE)
        try:
            data = json.loads(cleaned)
            if isinstance(data, dict):
                return {str(k): str(v) for k, v in data.items()}
        except json.JSONDecodeError:
            pass
        return {}

    def _summarise_source(self, max_chars: int = 6000) -> str:
        parts: list[str] = []
        total = 0
        for py_file in sorted(self.project_dir.rglob("*.py")):
            if "__pycache__" in str(py_file):
                continue
            try:
                content = py_file.read_text(encoding="utf-8")
                header = f"\n# === {py_file.relative_to(self.project_dir)} ===\n"
                chunk = header + content
                if total + len(chunk) > max_chars:
                    break
                parts.append(chunk)
                total += len(chunk)
            except Exception:
                pass
        return "".join(parts) or "(no source files)"

    # -----------------------------------------------------------------------
    # Failure archiving
    # -----------------------------------------------------------------------

    def _archive_failure(self, manifest: dict[str, Any], error_output: str) -> None:
        """Store the failure analysis in the ChromaDB vault for future reference."""
        try:
            from vault.vector_store import VectorStore
            vs = VectorStore()
            vs.archive_failure(
                project_id=manifest.get("project_id", "unknown"),
                project_name=manifest.get("name", "unknown"),
                error_summary=error_output[:2000],
                manifest=manifest,
            )
        except Exception as exc:
            log.warning(f"[TestLoop] Failed to archive to vault: {exc}")

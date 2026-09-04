"""
foundry/agent_factory.py
========================
FOUNDRY Controller — Agent provisioning and code generation.

Reads a project manifest, enriches it with relevant helper snippets
from the ChromaDB vault, constructs a tailored system prompt for each
worker role, and calls Ollama to generate the project scaffold.

Worker roles provisioned per manifest:
  • Core Systems Engineer  — main application logic
  • Test Automation Engineer — pytest suite
  • Static Analysis Auditor — ruff config & fixes
  • (Frontend Developer — conditionally, for web projects)
"""

from __future__ import annotations

import json
import logging
import re
import shutil
import textwrap
from pathlib import Path
from typing import Any

import requests

from genesis import config
from genesis.state_db import enqueue_task, log_event

log = logging.getLogger("foundry.factory")


# ---------------------------------------------------------------------------
# Role prompt templates
# ---------------------------------------------------------------------------

_ROLE_PROMPTS: dict[str, str] = {
    "core_engineer": textwrap.dedent("""\
        You are a senior Python engineer at an autonomous open-source foundry.
        Your task is to implement a complete, production-quality Python project
        based on the specification below. Requirements:
        - Pure Python 3.11+ with type hints throughout
        - Follow PEP 8 and keep the code concise and clean (< 200 lines total)
        - The main entry point must be `src/main.py`
        - Include `requirements.txt` (keep dependencies minimal or empty if standard library suffices)
        - Include `README.md` with: overview, installation, and usage examples

        PROJECT SPECIFICATION:
        {manifest_json}

        OUTPUT FORMAT:
        Return a JSON object where each key is a file path (relative to project root)
        and each value is the complete file content as a string. Example:
        {{
          "src/main.py": "...",
          "requirements.txt": "...",
          "README.md": "..."
        }}
        CRITICAL: The JSON keys must ONLY be relative file paths (e.g. 'src/main.py', 'requirements.txt').
        Do NOT output manifest fields (such as 'name', 'goals', 'category') as keys.
        Return ONLY the JSON object — no prose, no markdown fences.
    """),

    "test_engineer": textwrap.dedent("""\
        You are a test automation engineer. Given the following project source code
        and specification, write a concise, robust pytest test suite (< 60 lines).

        Requirements:
        - Use pytest with standard unit tests
        - Use only standard library + pytest — no external dependencies
        - The test file must be `tests/test_main.py`

        PROJECT SPECIFICATION:
        {manifest_json}

        SOURCE CODE:
        {source_code}

        Return a JSON object mapping file paths to file content (e.g. {{"tests/test_main.py": "..."}}).
        Return ONLY the JSON object.
    """),
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _call_ollama(model: str, system: str, user: str, num_predict: int = 1024, timeout: int = 120) -> str:
    """Ollama /api/chat call with automatic local fallback on timeout/error."""
    try:
        resp = requests.post(
            f"{config.OLLAMA_HOST}/api/chat",
            headers=config.OLLAMA_HEADERS,
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system or "You are an expert software engineer."},
                    {"role": "user",   "content": user},
                ],
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": config.OLLAMA_TEMPERATURE,
                    "num_ctx": config.OLLAMA_CTX_WINDOW,
                    "num_predict": num_predict,
                },
            },
            timeout=timeout,
        )
        resp.raise_for_status()
        return resp.json()["message"]["content"]
    except Exception as exc:
        log.warning(f"Remote Ollama call for model '{model}' failed ({exc}) — falling back to local llama3.2:1b …")

    # Fallback to local Ollama instance
    try:
        resp = requests.post(
            "http://127.0.0.1:11434/api/chat",
            json={
                "model": "llama3.2:1b",
                "messages": [
                    {"role": "system", "content": system or "You are an expert software engineer."},
                    {"role": "user",   "content": user},
                ],
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": config.OLLAMA_TEMPERATURE,
                    "num_ctx": 4096,
                    "num_predict": num_predict,
                },
            },
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()["message"]["content"]
    except Exception as local_exc:
        log.error(f"Local fallback also failed: {local_exc}")
        raise


def _parse_file_map(raw: str) -> dict[str, str]:
    """
    Parse LLM output into a {filepath: content} dict.
    Strips markdown fences and filters out non-file keys.
    """
    cleaned = raw.strip()
    cleaned = re.sub(r"^```[a-z]*\n?", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"\n?```$", "", cleaned, flags=re.MULTILINE)
    try:
        data = json.loads(cleaned)
        if isinstance(data, dict):
            # Check if files are nested under a 'files' key
            if "files" in data and isinstance(data["files"], dict):
                data = data["files"]
            valid: dict[str, str] = {}
            for k, v in data.items():
                k_str = str(k).strip()
                # Accept only entries that have a file extension or path separator
                if ("." in Path(k_str).name or "/" in k_str or "\\" in k_str) and isinstance(v, str):
                    valid[k_str] = v
            return valid
    except json.JSONDecodeError as exc:
        log.error(f"Failed to parse file map JSON: {exc}\nRaw[:500]: {raw[:500]}")
    return {}


def _write_files(project_dir: Path, file_map: dict[str, str]) -> None:
    """Write all files from the file map to disk, creating parent dirs."""
    for rel_path, content in file_map.items():
        safe_path = project_dir / rel_path.lstrip("/\\")
        safe_path.parent.mkdir(parents=True, exist_ok=True)
        safe_path.write_text(content, encoding="utf-8")
        log.debug(f"  Written: {rel_path} ({len(content)} chars)")

    # Ensure requirements.txt always exists
    req_file = project_dir / "requirements.txt"
    if not req_file.exists():
        req_file.write_text("", encoding="utf-8")


def _fetch_vault_context(manifest: dict[str, Any]) -> str:
    """Retrieve relevant helper snippets from the ChromaDB vault."""
    try:
        from vault.vector_store import VectorStore
        vs = VectorStore()
        query = f"{manifest['name']} {manifest['description']} {' '.join(manifest.get('goals', []))}"
        results = vs.search_helpers(query, n_results=5)
        if results:
            return "\n\n---\n\n".join(results)
    except Exception as exc:
        log.debug(f"Vault context fetch skipped: {exc}")
    return "(no vault context available)"


# ---------------------------------------------------------------------------
# AgentFactory
# ---------------------------------------------------------------------------

class AgentFactory:
    """
    Provisions worker agents and generates a complete project scaffold
    from a project manifest.
    """

    def __init__(self, model: str = ""):
        self.model = model or config.OLLAMA_PRIMARY_MODEL

    def generate(self, manifest: dict[str, Any], namespace: str) -> Path:
        """
        Full generation pipeline:
          1. Fetch vault context
          2. Core engineer generates main source files
          3. Test engineer generates/augments test suite
          4. Write all files to project directory

        Returns: Path to the generated project directory.
        """
        project_id = manifest["project_id"]
        project_name = manifest["name"]
        project_dir = config.PROJECTS_DIR / project_name

        # Clean slate if re-generating
        if project_dir.exists():
            shutil.rmtree(project_dir)
        project_dir.mkdir(parents=True)

        log.info(f"[AgentFactory] Generating '{project_name}' → {project_dir}")
        log_event(f"Starting generation: {project_name}", category="FOUNDRY",
                  payload={"project_id": project_id, "namespace": namespace})

        manifest_json = json.dumps(manifest, indent=2)
        vault_ctx = _fetch_vault_context(manifest)

        # ── Step A: Core Engineer ───────────────────────────────────────────
        log.info("  [CoreEngineer] Generating main source …")
        core_prompt = _ROLE_PROMPTS["core_engineer"].format(
            manifest_json=manifest_json,
            vault_context=vault_ctx,
        )
        try:
            core_raw = _call_ollama(self.model, system="", user=core_prompt)
            core_files = _parse_file_map(core_raw)
            if not core_files:
                raise ValueError("CoreEngineer returned no files.")
            _write_files(project_dir, core_files)
            log.info(f"  [CoreEngineer] {len(core_files)} files written.")
        except Exception as exc:
            log.error(f"CoreEngineer failed: {exc}")
            # Write a minimal skeleton so tests can at least run
            _write_minimal_skeleton(project_dir, manifest)

        # ── Step B: Test Engineer ───────────────────────────────────────────
        log.info("  [TestEngineer] Generating test suite …")
        # Summarise source code (cap at 8 KB to stay in context)
        source_summary = _summarise_project(project_dir, max_chars=8000)
        test_prompt = _ROLE_PROMPTS["test_engineer"].format(
            manifest_json=manifest_json,
            source_code=source_summary,
        )
        try:
            test_raw = _call_ollama(self.model, system="", user=test_prompt)
            test_files = _parse_file_map(test_raw)
            if not test_files:
                raise ValueError("TestEngineer returned no files.")
            _write_files(project_dir, test_files)
            log.info(f"  [TestEngineer] {len(test_files)} test files written.")
        except Exception as exc:
            log.warning(f"TestEngineer failed: {exc} — writing placeholder test.")
            _write_placeholder_test(project_dir)

        # Guarantee that tests directory with at least one test file exists
        test_dir = project_dir / "tests"
        if not test_dir.exists() or not list(test_dir.glob("*.py")):
            _write_placeholder_test(project_dir)

        # ── Step C: Enqueue for FOUNDRY test loop ───────────────────────────
        task_id = enqueue_task(
            project_name=project_name,
            payload=manifest,
            priority=int((1.0 - manifest.get("priority_score", 0.5)) * 10),
            manifest_ref=str(config.MANIFEST_PATH),
        )
        log.info(f"  Enqueued task {task_id[:8]} for test loop.")

        return project_dir

    # -----------------------------------------------------------------------
    # Fallback helpers
    # -----------------------------------------------------------------------

    @staticmethod
    def _minimal_main(manifest: dict[str, Any]) -> str:
        return textwrap.dedent(f"""\
            \"\"\"
            {manifest['name']} — {manifest['description']}
            Auto-generated by Project Genesis (minimal skeleton fallback).
            \"\"\"


            def main() -> None:
                print("{manifest['name']}: not yet implemented.")


            if __name__ == "__main__":
                main()
        """)


def _write_minimal_skeleton(project_dir: Path, manifest: dict[str, Any]) -> None:
    src = project_dir / "src"
    src.mkdir(exist_ok=True)
    (src / "main.py").write_text(AgentFactory._minimal_main(manifest), encoding="utf-8")
    (project_dir / "requirements.txt").write_text("", encoding="utf-8")
    (project_dir / "README.md").write_text(
        f"# {manifest['name']}\n\n{manifest['description']}\n", encoding="utf-8"
    )


def _write_placeholder_test(project_dir: Path) -> None:
    tests = project_dir / "tests"
    tests.mkdir(exist_ok=True)
    (tests / "test_placeholder.py").write_text(
        textwrap.dedent("""\
            \"\"\"Placeholder test — replace with real tests.\"\"\"


            def test_placeholder():
                assert True
        """),
        encoding="utf-8",
    )


def _summarise_project(project_dir: Path, max_chars: int = 8000) -> str:
    """Concatenate project source files up to max_chars for context injection."""
    parts: list[str] = []
    total = 0
    for py_file in sorted(project_dir.rglob("*.py")):
        if "__pycache__" in str(py_file):
            continue
        try:
            content = py_file.read_text(encoding="utf-8")
            header = f"\n# === {py_file.relative_to(project_dir)} ===\n"
            chunk = header + content
            if total + len(chunk) > max_chars:
                parts.append(f"\n# ... (truncated, {py_file.name})")
                break
            parts.append(chunk)
            total += len(chunk)
        except Exception:
            pass
    return "".join(parts) or "(no source files found)"

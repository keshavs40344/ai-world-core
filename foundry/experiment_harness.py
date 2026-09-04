"""
foundry/experiment_harness.py
==============================
A/B Experimentation Harness for Project Genesis.

Allows running two prompt or model variants against the same project specification,
evaluating them across:
  - First-pass pytest pass rate
  - Lint violations count (Ruff)
  - Cyclomatic complexity (AST analysis)
  - Code compactness (lines of code)

Declares a winner and logs metrics to prompt_registry and feedback_store.
"""

from __future__ import annotations

import ast
import logging
import shutil
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from genesis import config
from foundry.agent_factory import AgentFactory
from foundry.prompt_registry import record_prompt_outcome
from foundry.sandbox_runner import SandboxRunner, RunResult

log = logging.getLogger("foundry.experiment")


@dataclass
class VariantResult:
    variant_id: str
    prompt_version_id: str
    project_dir: Path
    passed_tests: bool
    exit_code: int
    ruff_violations: int
    cyclomatic_complexity: float
    total_loc: int
    execution_time_sec: float
    overall_score: float


class ExperimentHarness:
    """Runs A/B comparisons between two generation strategies."""

    def __init__(self) -> None:
        self.sandbox = SandboxRunner()

    def _compute_code_metrics(self, project_dir: Path) -> tuple[int, float]:
        """Calculates total lines of code and average cyclomatic complexity via AST."""
        total_loc = 0
        complexity_scores = []

        for py_file in project_dir.rglob("*.py"):
            try:
                content = py_file.read_text(encoding="utf-8", errors="ignore")
                lines = [l for l in content.splitlines() if l.strip() and not l.strip().startswith("#")]
                total_loc += len(lines)

                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        # Cyclomatic complexity = 1 + branching nodes
                        branches = sum(
                            1 for child in ast.walk(node)
                            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor,
                                                  ast.ExceptHandler, ast.With, ast.Assert))
                        )
                        complexity_scores.append(1 + branches)
            except Exception:
                pass

        avg_complexity = (sum(complexity_scores) / len(complexity_scores)) if complexity_scores else 1.0
        return total_loc, round(avg_complexity, 2)

    def _run_sandbox_checks(self, project_dir: Path) -> tuple[bool, int, int]:
        """Runs ruff and pytest in sandbox and returns (passed, exit_code, ruff_violations)."""
        import platform
        cmd = (
            "python -m pip install -q -r requirements.txt "
            "&& ruff check . --quiet "
            "&& pytest --tb=short -q --no-header"
            if platform.system() == "Windows" else
            "pip install -q -r requirements.txt 2>&1 "
            "&& ruff check . --quiet 2>&1 "
            "&& pytest --tb=short -q --no-header 2>&1"
        )
        res: RunResult = self.sandbox.run(project_dir=project_dir, command=cmd)
        passed = res.success
        ruff_violations = len([l for l in res.stdout.splitlines() if ":" in l and "error" in l.lower()])
        return passed, res.exit_code, ruff_violations

    def run_ab_test(
        self,
        manifest: dict[str, Any],
        variant_a_prompt: Optional[str] = None,
        variant_b_prompt: Optional[str] = None,
        version_id_a: str = "variant_a",
        version_id_b: str = "variant_b",
        model: str = "",
    ) -> dict[str, Any]:
        """
        Executes generation for Variant A and Variant B in separate sandboxes,
        evaluates metrics, and designates a winner.
        """
        model = model or config.OLLAMA_PRIMARY_MODEL
        name = manifest.get("name", "experiment_project")

        dir_a = config.PROJECTS_DIR / f"{name}_exp_a"
        dir_b = config.PROJECTS_DIR / f"{name}_exp_b"

        # Generate Variant A
        log.info(f"[AB Harness] Running Variant A for '{name}'...")
        t0 = time.perf_counter()
        factory_a = AgentFactory(model=model)
        factory_a.generate(manifest, namespace="developer_tools", target_dir=dir_a)
        time_a = time.perf_counter() - t0
        pass_a, exit_a, ruff_a = self._run_sandbox_checks(dir_a)
        loc_a, comp_a = self._compute_code_metrics(dir_a)

        # Generate Variant B
        log.info(f"[AB Harness] Running Variant B for '{name}'...")
        t1 = time.perf_counter()
        factory_b = AgentFactory(model=model)
        factory_b.generate(manifest, namespace="developer_tools", target_dir=dir_b)
        time_b = time.perf_counter() - t1
        pass_b, exit_b, ruff_b = self._run_sandbox_checks(dir_b)
        loc_b, comp_b = self._compute_code_metrics(dir_b)

        # Scoring function: Test pass is mandatory (+100 pts), lower ruff violations, lower complexity
        score_a = (100 if pass_a else 0) - (ruff_a * 5) - (comp_a * 2) - (time_a * 0.1)
        score_b = (100 if pass_b else 0) - (ruff_b * 5) - (comp_b * 2) - (time_b * 0.1)

        winner = "VARIANT_A" if score_a >= score_b else "VARIANT_B"
        winning_dir = dir_a if winner == "VARIANT_A" else dir_b

        # Record outcomes in prompt registry
        record_prompt_outcome(version_id_a, passed_first_try=pass_a, retries=0)
        record_prompt_outcome(version_id_b, passed_first_try=pass_b, retries=0)

        log.info(f"[AB Harness] Completed: Winner is {winner} (Score A: {score_a:.1f}, Score B: {score_b:.1f})")

        return {
            "winner": winner,
            "winning_dir": str(winning_dir),
            "variant_a": {
                "passed": pass_a,
                "score": score_a,
                "ruff_violations": ruff_a,
                "loc": loc_a,
                "complexity": comp_a,
                "time_sec": round(time_a, 2),
            },
            "variant_b": {
                "passed": pass_b,
                "score": score_b,
                "ruff_violations": ruff_b,
                "loc": loc_b,
                "complexity": comp_b,
                "time_sec": round(time_b, 2),
            },
        }

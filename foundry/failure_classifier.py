"""
foundry/failure_classifier.py
==============================
Failure Taxonomy Classifier for Project Genesis.

Analyzes raw execution output (pytest traces, ruff violation lines, Python tracebacks)
and classifies them into standardized taxonomy categories for pattern memory
and dashboard trend analysis.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

# Standardized Genesis failure taxonomy categories
CATEGORY_ASYNC_MISUSE        = "ASYNC_MISUSE"
CATEGORY_MISSING_ERROR_HAND  = "MISSING_ERROR_HANDLING"
CATEGORY_IMPORT_DEPENDENCY   = "IMPORT_DEPENDENCY_ERROR"
CATEGORY_TYPE_MISMATCH       = "TYPE_MISMATCH"
CATEGORY_TEST_ASSERTION      = "TEST_ASSERTION_FAILURE"
CATEGORY_TIMEOUT_PERF        = "TIMEOUT_PERFORMANCE"
CATEGORY_RUFF_VIOLATION      = "LINTER_RUFF_VIOLATION"
CATEGORY_SYNTAX_ERROR        = "SYNTAX_ERROR"
CATEGORY_UNKNOWN             = "UNKNOWN_FAILURE"

_RUFF_CODE_REGEX = re.compile(r"\b([EFWIBCNPDQSRUTAY]\d{3,4})\b")


@dataclass
class ClassificationResult:
    category: str
    summary: str
    ruff_rules: list[str]
    confidence: float


def classify_failure(raw_log: str) -> ClassificationResult:
    """
    Classifies error logs into a Failure Taxonomy Category using heuristic
    pattern matching, extracting ruff codes and key failure summaries.
    """
    if not raw_log:
        return ClassificationResult(
            category=CATEGORY_UNKNOWN,
            summary="Empty or absent error output",
            ruff_rules=[],
            confidence=0.1,
        )

    log_lower = raw_log.lower()
    ruff_rules = list(set(_RUFF_CODE_REGEX.findall(raw_log)))

    # 1. Syntax / Parsing Errors
    if "syntaxerror" in log_lower or "indentationerror" in log_lower:
        m = re.search(r"SyntaxError: ([^\n]+)", raw_log) or re.search(r"IndentationError: ([^\n]+)", raw_log)
        summary = f"Syntax error: {m.group(1)}" if m else "Invalid Python syntax or indentation"
        return ClassificationResult(CATEGORY_SYNTAX_ERROR, summary, ruff_rules, 0.95)

    # 2. Async/Await misuse
    if "runtimeerror: this event loop is already running" in log_lower or \
       "coroutine" in log_lower and ("was never awaited" in log_lower or "cannot be called from" in log_lower) or \
       "attached to a different loop" in log_lower:
        summary = "Misuse of asyncio / event loop or unawaited coroutine"
        return ClassificationResult(CATEGORY_ASYNC_MISUSE, summary, ruff_rules, 0.9)

    # 3. Missing imports / dependency errors
    if "modulenotfounderror" in log_lower or "importerror" in log_lower:
        m = re.search(r"(?:ModuleNotFoundError|ImportError): ([^\n]+)", raw_log)
        summary = f"Import error: {m.group(1)}" if m else "Missing module dependency or invalid import"
        return ClassificationResult(CATEGORY_IMPORT_DEPENDENCY, summary, ruff_rules, 0.95)

    # 4. Type errors / NoneType attribute errors
    if "typeerror" in log_lower or "attributeerror: 'nonetype' object" in log_lower:
        m = re.search(r"(?:TypeError|AttributeError): ([^\n]+)", raw_log)
        summary = f"Type mismatch: {m.group(1)}" if m else "Type mismatch or unexpected None reference"
        return ClassificationResult(CATEGORY_TYPE_MISMATCH, summary, ruff_rules, 0.85)

    # 5. Ruff Linter violations
    if ("ruff check" in log_lower or "found" in log_lower and "error" in log_lower) and ruff_rules:
        summary = f"Linter violations ({len(ruff_rules)} rules violated: {', '.join(ruff_rules[:4])})"
        return ClassificationResult(CATEGORY_RUFF_VIOLATION, summary, ruff_rules, 0.9)

    # 6. Pytest assertion failures
    if "assertionerror" in log_lower or "assert " in raw_log or "failed in" in log_lower:
        m = re.search(r"AssertionError:? ([^\n]*)", raw_log)
        detail = m.group(1).strip() if m and m.group(1).strip() else "Unit test assertion failed"
        summary = f"Pytest assertion failure: {detail}"
        return ClassificationResult(CATEGORY_TEST_ASSERTION, summary, ruff_rules, 0.85)

    # 7. Unhandled exceptions / missing error handling
    if "traceback (most recent call last)" in log_lower and ("filenotfounderror" in log_lower or "keyerror" in log_lower or "valueerror" in log_lower):
        m = re.search(r"(?:FileNotFoundError|KeyError|ValueError): ([^\n]+)", raw_log)
        summary = f"Missing error handling for: {m.group(1)}" if m else "Unhandled runtime exception"
        return ClassificationResult(CATEGORY_MISSING_ERROR_HAND, summary, ruff_rules, 0.8)

    # 8. Timeout or performance bottleneck
    if "timeout" in log_lower or "timed out" in log_lower:
        summary = "Execution timed out in sandbox environment"
        return ClassificationResult(CATEGORY_TIMEOUT_PERF, summary, ruff_rules, 0.8)

    # Fallback
    first_error_line = "General test or linter failure"
    for line in raw_log.splitlines():
        if "error" in line.lower() or "fail" in line.lower():
            first_error_line = line.strip()[:100]
            break

    return ClassificationResult(CATEGORY_UNKNOWN, first_error_line, ruff_rules, 0.5)

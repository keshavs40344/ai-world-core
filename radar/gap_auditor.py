"""
radar/gap_auditor.py
====================
RADAR Controller — Step 2: Gap & Optimization Analysis.

Takes raw TrendSignals from the scanner, batches them into a concise
summary, and asks the local Ollama LLM to identify:
  - Structural bottlenecks and gaps in popular tooling
  - Opportunities for local-first, open-source alternatives
  - Projects well-suited for autonomous generation by FOUNDRY

Returns a ranked list of `Opportunity` objects ready for ManifestWriter.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any

import requests

from genesis import config
from radar.scanner import TrendSignal

log = logging.getLogger("radar.auditor")


# ---------------------------------------------------------------------------
# Data structure
# ---------------------------------------------------------------------------

@dataclass
class Opportunity:
    name: str
    category: str
    subcategory: str
    description: str
    rationale: str                      # why this gap exists / why now
    goals: list[str] = field(default_factory=list)
    estimated_complexity: str = "medium"  # low | medium | high
    priority_score: float = 0.5          # 0.0 – 1.0
    source_signals: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """\
You are a senior software architect and market analyst for an autonomous \
open-source software foundry. Your job is to identify high-value, \
buildable software opportunities from a set of trend signals.

Rules:
- Only suggest projects that can be built with Python/JavaScript/Go using \
  open-source libraries.
- Prioritise LOCAL-FIRST tools (no mandatory cloud), CLI utilities, \
  developer micro-services, data processing pipelines, and lightweight \
  desktop apps.
- Each opportunity must be unique, concrete, and achievable in under 2,000 \
  lines of code.
- Avoid suggestions that require proprietary APIs, licensed datasets, \
  or significant UI design work.
- Return ONLY a valid JSON array — no prose, no markdown fences.
"""

_USER_PROMPT_TEMPLATE = """\
Here are {n} trend signals from PyPI, GitHub, and HuggingFace:

{signals_json}

Identify the top {k} software opportunities — gaps, inefficiencies, or \
missing local-first alternatives you observe in this landscape.

Return a JSON array of objects with these exact fields:
{{
  "name": "Short project name (snake_case)",
  "category": "Top-level domain e.g. Developer Tools",
  "subcategory": "e.g. Performance Monitoring",
  "description": "One sentence describing what the tool does",
  "rationale": "Why this gap exists and why building it now is valuable",
  "goals": ["goal 1", "goal 2", "goal 3"],
  "estimated_complexity": "low|medium|high",
  "priority_score": 0.0-1.0,
  "source_signals": ["signal name 1", "signal name 2"]
}}
"""


def _signals_to_summary(signals: list[TrendSignal]) -> list[dict[str, Any]]:
    """Convert TrendSignal objects to a compact JSON-serialisable dict."""
    return [
        {
            "source": s.source,
            "name": s.name,
            "description": s.description[:80],
            "score": round(s.score, 3),
            "tags": s.tags[:3],
        }
        for s in signals[:3]   # Top 3 signals for fast, reliable remote inference
    ]


# ---------------------------------------------------------------------------
# Ollama call (with retry on fallback model)
# ---------------------------------------------------------------------------

def _call_ollama(model: str, messages: list[dict], retries: int = 2) -> str:
    """Send a chat request to Ollama, returning the raw response string."""
    for attempt in range(retries + 1):
        try:
            resp = requests.post(
                f"{config.OLLAMA_HOST}/api/chat",
                headers=config.OLLAMA_HEADERS,
                json={
                    "model": model,
                    "messages": messages,
                    "stream": False,
                    "format": "json",
                    "options": {
                        "temperature": config.OLLAMA_TEMPERATURE,
                        "num_ctx": config.OLLAMA_CTX_WINDOW,
                        "num_predict": 512,
                    },
                },
                timeout=300,
            )
            resp.raise_for_status()
            return resp.json()["message"]["content"]
        except Exception as exc:
            log.warning(f"Ollama call attempt {attempt+1} failed: {exc}")
            if attempt == retries:
                raise
            # Try fallback model
            for fallback in config.OLLAMA_FALLBACK_MODELS:
                if fallback != model:
                    log.info(f"Stepping down to fallback model: {fallback}")
                    try:
                        return _call_ollama(fallback, messages, retries=0)
                    except Exception:
                        pass
            raise


# ---------------------------------------------------------------------------
# Auditor implementation
# ---------------------------------------------------------------------------

class GapAuditor:
    """
    Synthesises market signals into concrete Opportunity objects using Ollama.
    """

    def __init__(self, model: str | None = None) -> None:
        self.model = model or config.OLLAMA_PRIMARY_MODEL

    def analyse(self, signals: list[TrendSignal], top_k: int = 1) -> list[Opportunity]:
        """
        Analyse trend signals and return up to top_k Opportunity objects,
        sorted by priority_score descending.
        """
        if not signals:
            log.warning("No signals provided to GapAuditor — returning empty list.")
            return []

        summaries = _signals_to_summary(signals)
        user_prompt = _USER_PROMPT_TEMPLATE.format(
            n=len(summaries),
            signals_json=json.dumps(summaries, indent=2),
            k=top_k,
        )

        messages = [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user",   "content": user_prompt},
        ]

        log.info(f"[GapAuditor] Sending {len(summaries)} signals to {self.model} …")
        raw = _call_ollama(self.model, messages)

        opportunities = self._parse_response(raw, signals)
        opportunities.sort(key=lambda o: o.priority_score, reverse=True)
        log.info(f"[GapAuditor] {len(opportunities)} opportunities identified.")
        return opportunities[:top_k]

    def _parse_response(
        self, raw: str, signals: list[TrendSignal]
    ) -> list[Opportunity]:
        """Parse the LLM JSON response into Opportunity objects."""
        try:
            # Strip any accidental markdown fences
            cleaned = raw.strip()
            if cleaned.startswith("```"):
                cleaned = "\n".join(cleaned.split("\n")[1:])
            if cleaned.endswith("```"):
                cleaned = cleaned.rsplit("```", 1)[0]

            data = json.loads(cleaned)
            if not isinstance(data, list):
                data = [data]

            signal_names = {s.name for s in signals}
            results = []
            for item in data:
                try:
                    opp = Opportunity(
                        name=item.get("name", "unnamed_project"),
                        category=item.get("category", "Uncategorized"),
                        subcategory=item.get("subcategory", "General"),
                        description=item.get("description", ""),
                        rationale=item.get("rationale", ""),
                        goals=item.get("goals", []),
                        estimated_complexity=item.get("estimated_complexity", "medium"),
                        priority_score=float(item.get("priority_score", 0.5)),
                        source_signals=[
                            s for s in item.get("source_signals", [])
                            if s in signal_names
                        ],
                    )
                    results.append(opp)
                except Exception as parse_exc:
                    log.warning(f"Skipping malformed opportunity entry: {parse_exc}")

            return results

        except json.JSONDecodeError as exc:
            log.error(f"Failed to parse LLM response as JSON: {exc}\nRaw: {raw[:500]}")
            return []

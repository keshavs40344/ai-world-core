"""
genesis/dynamic_config.py
==========================
Self-Tuning & Dynamic Configuration Manager for Project Genesis.

Monitors recent system health, sliding-window pass rates, and host hardware
resources to dynamically adjust:
  - CIRCUIT_BREAKER_LIMIT (e.g. increase retry attempts when LLM needs healing, tighten when healthy)
  - MAX_CONCURRENT_WORKERS (based on available RAM & CPU count)
  - MODEL_FALLBACK_ORDER (prioritizing high-success models)
"""

from __future__ import annotations

import logging
import os
import psutil
from dataclasses import dataclass
from typing import Any

from genesis import config
from foundry.feedback_store import get_category_performance_stats

log = logging.getLogger("genesis.dynamic_config")


@dataclass
class TunedParameters:
    circuit_breaker_limit: int
    max_concurrent_workers: int
    active_model: str
    pass_rate_window: float
    tuning_rationale: str


class DynamicConfigManager:
    """Calculates optimal runtime configurations on the fly."""

    def __init__(self, sample_window: int = 15) -> None:
        self.sample_window = sample_window

    def get_tuned_parameters() -> TunedParameters:
        return DynamicConfigManager().tune()

    def tune(self) -> TunedParameters:
        ram_gb = psutil.virtual_memory().available / (1024 ** 3)
        cpu_count = os.cpu_count() or 4

        # Baseline defaults
        breaker_limit = config.CIRCUIT_BREAKER_LIMIT
        workers = config.MAX_CONCURRENT_WORKERS
        active_model = config.OLLAMA_PRIMARY_MODEL
        rationale_parts = []

        # Analyze recent performance across categories
        stats = get_category_performance_stats()
        total_runs = sum(s["total_runs"] for s in stats.values())
        total_passes = sum(s["passes"] for s in stats.values())
        overall_pass_rate = (total_passes / total_runs) if total_runs > 0 else 0.8

        # 1. Circuit Breaker tuning
        if total_runs >= 3:
            if overall_pass_rate < 0.50:
                # LLM struggling; give more healing attempts before circuit-breaking
                breaker_limit = min(7, config.CIRCUIT_BREAKER_LIMIT + 2)
                rationale_parts.append(f"Low pass rate ({overall_pass_rate:.1%}): raised circuit breaker to {breaker_limit}")
            elif overall_pass_rate > 0.85:
                # High reliability; tighten breaker to save compute
                breaker_limit = max(3, config.CIRCUIT_BREAKER_LIMIT - 1)
                rationale_parts.append(f"High pass rate ({overall_pass_rate:.1%}): optimized circuit breaker to {breaker_limit}")
        else:
            rationale_parts.append("Using default circuit breaker limit (insufficient history)")

        # 2. Worker concurrency tuning based on RAM & CPU
        if ram_gb >= 12.0 and cpu_count >= 8:
            workers = min(4, max(config.MAX_CONCURRENT_WORKERS, 3))
            rationale_parts.append(f"High RAM ({ram_gb:.1f}GB): scaling workers to {workers}")
        elif ram_gb < 4.0:
            workers = 1
            rationale_parts.append(f"Constrained RAM ({ram_gb:.1f}GB): restricted workers to 1")
        else:
            workers = config.MAX_CONCURRENT_WORKERS

        # 3. Model selection based on memory pressure
        if ram_gb < config.OLLAMA_RAM_THRESHOLD_GB:
            for fallback in config.OLLAMA_FALLBACK_MODELS:
                active_model = fallback
                rationale_parts.append(f"RAM below threshold: switched active model to fallback '{fallback}'")
                break

        return TunedParameters(
            circuit_breaker_limit=breaker_limit,
            max_concurrent_workers=workers,
            active_model=active_model,
            pass_rate_window=round(overall_pass_rate, 3),
            tuning_rationale=" | ".join(rationale_parts),
        )

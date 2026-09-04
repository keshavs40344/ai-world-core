"""
resilient_token_bucket_limiter - Core Engine
============================================
Thread-safe, sovereign, zero-external-dependency Leaky Bucket & Token Bucket
rate-limiter with jitter, automated burst regulation, and adaptive backoff.
"""

from __future__ import annotations

import random
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeVar

T = TypeVar("T")


@dataclass
class LimiterMetrics:
    total_requested: int = 0
    total_allowed: int = 0
    total_throttled: int = 0
    total_wait_time_sec: float = 0.0


class ResilientTokenBucket:
    """
    High-precision token bucket rate limiter with concurrency locks and jitter.
    """

    def __init__(
        self,
        rate_per_sec: float,
        burst_capacity: int,
        jitter_range: tuple[float, float] = (0.01, 0.05),
    ):
        if rate_per_sec <= 0:
            raise ValueError("rate_per_sec must be positive.")
        if burst_capacity < 1:
            raise ValueError("burst_capacity must be at least 1.")

        self.rate_per_sec = float(rate_per_sec)
        self.capacity = float(burst_capacity)
        self.tokens = float(burst_capacity)
        self.jitter_range = jitter_range
        self.last_refill = time.monotonic()
        self._lock = threading.Lock()
        self.metrics = LimiterMetrics()

    def _refill(self) -> None:
        now = time.monotonic()
        delta = now - self.last_refill
        if delta > 0:
            added = delta * self.rate_per_sec
            self.tokens = min(self.capacity, self.tokens + added)
            self.last_refill = now

    def acquire(self, tokens: int = 1, block: bool = True, timeout: float | None = None) -> bool:
        """
        Attempts to acquire specified number of tokens.
        If block is True, waits with jitter until available or timeout expires.
        """
        if tokens < 1:
            raise ValueError("tokens requested must be >= 1.")

        start_wait = time.monotonic()
        with self._lock:
            self.metrics.total_requested += 1

            while True:
                self._refill()
                if self.tokens >= tokens:
                    self.tokens -= tokens
                    self.metrics.total_allowed += 1
                    return True

                if not block:
                    self.metrics.total_throttled += 1
                    return False

                # Calculate remaining wait time
                needed = tokens - self.tokens
                base_wait = needed / self.rate_per_sec
                jitter = random.uniform(*self.jitter_range)
                wait_duration = base_wait + jitter

                if timeout is not None:
                    elapsed = time.monotonic() - start_wait
                    if elapsed + wait_duration > timeout:
                        self.metrics.total_throttled += 1
                        return False

                # Release lock while sleeping to permit concurrent refills
                self._lock.release()
                try:
                    time.sleep(wait_duration)
                    self.metrics.total_wait_time_sec += wait_duration
                finally:
                    self._lock.acquire()

    def execute_throttled(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Helper to invoke a callable wrapped inside rate regulation."""
        self.acquire(tokens=1, block=True)
        return func(*args, **kwargs)

    def get_metrics(self) -> dict[str, float | int]:
        """Snapshot current limiter metrics."""
        with self._lock:
            return {
                "total_requested": self.metrics.total_requested,
                "total_allowed": self.metrics.total_allowed,
                "total_throttled": self.metrics.total_throttled,
                "total_wait_time_sec": round(self.metrics.total_wait_time_sec, 4),
                "available_tokens": round(self.tokens, 2),
            }

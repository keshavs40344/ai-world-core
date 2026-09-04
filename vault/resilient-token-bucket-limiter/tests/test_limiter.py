"""Comprehensive QA test suite for ResilientTokenBucket."""
import concurrent.futures
import time

import pytest
from src.limiter import ResilientTokenBucket


def test_initial_burst_capacity():
    limiter = ResilientTokenBucket(rate_per_sec=10.0, burst_capacity=5)
    for _ in range(5):
        assert limiter.acquire(1, block=False) is True
    # Next immediate request with block=False must be throttled
    assert limiter.acquire(1, block=False) is False


def test_refill_mechanism():
    limiter = ResilientTokenBucket(rate_per_sec=20.0, burst_capacity=2)
    assert limiter.acquire(2, block=False) is True
    assert limiter.acquire(1, block=False) is False
    # Wait for 1 token refill (1/20 = 0.05s)
    time.sleep(0.08)
    assert limiter.acquire(1, block=False) is True


def test_timeout_expiration():
    limiter = ResilientTokenBucket(rate_per_sec=1.0, burst_capacity=1)
    assert limiter.acquire(1, block=False) is True
    # Asking for 1 token with timeout 0.05s on a 1 token/sec bucket should time out
    assert limiter.acquire(1, block=True, timeout=0.05) is False


def test_concurrent_thread_safety():
    limiter = ResilientTokenBucket(rate_per_sec=50.0, burst_capacity=10)
    workers = 5
    requests_per_worker = 10

    def task():
        acquired = 0
        for _ in range(requests_per_worker):
            if limiter.acquire(1, block=True, timeout=2.0):
                acquired += 1
        return acquired

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        results = list(executor.map(lambda _: task(), range(workers)))

    assert sum(results) == workers * requests_per_worker
    metrics = limiter.get_metrics()
    assert metrics["total_allowed"] == workers * requests_per_worker


def test_invalid_parameters():
    with pytest.raises(ValueError):
        ResilientTokenBucket(rate_per_sec=-1.0, burst_capacity=5)
    with pytest.raises(ValueError):
        ResilientTokenBucket(rate_per_sec=10.0, burst_capacity=0)
    limiter = ResilientTokenBucket(rate_per_sec=10.0, burst_capacity=5)
    with pytest.raises(ValueError):
        limiter.acquire(0)

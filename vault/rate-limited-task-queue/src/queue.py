"""
Core Queue implementation with Token Bucket Rate Limiting.
"""
from __future__ import annotations

import heapq
import itertools
import threading
import time
import uuid
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, Callable, Dict, Optional


class TaskPriority(IntEnum):
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4


@dataclass(order=True)
class PrioritizedItem:
    priority: int
    count: int
    task: "Task" = field(compare=False)


@dataclass
class Task:
    name: str
    payload: dict[str, Any] = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: str = "PENDING"  # PENDING | IN_PROGRESS | COMPLETED | FAILED
    attempts: int = 0
    max_retries: int = 3
    created_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    result: Any = None
    error: Optional[str] = None


class TokenBucketRateLimiter:
    """
    Thread-safe Token Bucket Rate Limiter.
    Allows burst processing up to capacity, while enforcing a continuous rate.
    """

    def __init__(self, rate: float, capacity: float):
        if rate <= 0:
            raise ValueError("Rate must be positive")
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        self.rate = float(rate)
        self.capacity = float(capacity)
        self.tokens = float(capacity)
        self.last_update = time.time()
        self._lock = threading.Lock()

    def acquire(self, tokens: float = 1.0, blocking: bool = True, timeout: float = 5.0) -> bool:
        start_time = time.time()
        while True:
            with self._lock:
                now = time.time()
                elapsed = now - self.last_update
                self.last_update = now
                self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)

                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return True

                if not blocking:
                    return False

                needed = tokens - self.tokens
                wait_time = needed / self.rate

            if time.time() - start_time + wait_time > timeout:
                return False
            time.sleep(min(wait_time, 0.05))


class RateLimitedTaskQueue:
    """
    Priority-driven task queue with integrated rate-limiting.
    """

    def __init__(self, rate_per_sec: float = 50.0, burst_capacity: float = 10.0):
        self.limiter = TokenBucketRateLimiter(rate=rate_per_sec, capacity=burst_capacity)
        self._heap: list[PrioritizedItem] = []
        self._tasks_by_id: dict[str, Task] = {}
        self._counter = itertools.count()
        self._lock = threading.Lock()

    def enqueue(self, task: Task) -> str:
        with self._lock:
            count = next(self._counter)
            item = PrioritizedItem(priority=task.priority.value, count=count, task=task)
            heapq.heappush(self._heap, item)
            self._tasks_by_id[task.id] = task
            return task.id

    def dequeue(self, blocking: bool = True, timeout: float = 5.0) -> Optional[Task]:
        """Acquires a rate limit token and retrieves the highest-priority task."""
        if not self.limiter.acquire(tokens=1.0, blocking=blocking, timeout=timeout):
            return None

        with self._lock:
            if not self._heap:
                return None
            item = heapq.heappop(self._heap)
            task = item.task
            task.status = "IN_PROGRESS"
            task.attempts += 1
            return task

    def get_task(self, task_id: str) -> Optional[Task]:
        with self._lock:
            return self._tasks_by_id.get(task_id)

    def size(self) -> int:
        with self._lock:
            return len(self._heap)

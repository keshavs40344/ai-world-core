"""
Worker pool and task execution loop.
"""
from __future__ import annotations

import logging
import threading
import time
from typing import Any, Callable, Dict, List, Optional
from .queue import RateLimitedTaskQueue, Task

log = logging.getLogger("microservice.worker")


class Worker:
    """
    Worker thread consuming tasks from RateLimitedTaskQueue.
    """

    def __init__(
        self,
        worker_id: str,
        queue: RateLimitedTaskQueue,
        handler: Optional[Callable[[Task], Any]] = None,
    ):
        self.worker_id = worker_id
        self.queue = queue
        self.handler = handler or self._default_handler
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self.tasks_processed = 0
        self.tasks_failed = 0

    def _default_handler(self, task: Task) -> Any:
        # Echo task execution
        return {"task_id": task.id, "processed_by": self.worker_id, "timestamp": time.time()}

    def start(self) -> None:
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, name=f"worker-{self.worker_id}", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)

    def _run_loop(self) -> None:
        while self._running:
            task = self.queue.dequeue(blocking=True, timeout=0.1)
            if task is None:
                time.sleep(0.01)
                continue

            try:
                result = self.handler(task)
                task.result = result
                task.status = "COMPLETED"
                task.completed_at = time.time()
                self.tasks_processed += 1
            except Exception as exc:
                log.warning(f"Task {task.id} failed: {exc}")
                task.error = str(exc)
                if task.attempts < task.max_retries:
                    task.status = "PENDING"
                    self.queue.enqueue(task)
                else:
                    task.status = "FAILED"
                    self.tasks_failed += 1


class WorkerPool:
    """
    Manages a pool of concurrent Worker instances.
    """

    def __init__(
        self,
        queue: RateLimitedTaskQueue,
        num_workers: int = 4,
        handler: Optional[Callable[[Task], Any]] = None,
    ):
        self.queue = queue
        self.workers = [
            Worker(worker_id=f"w{i+1}", queue=queue, handler=handler)
            for i in range(num_workers)
        ]

    def start(self) -> None:
        for w in self.workers:
            w.start()

    def stop(self) -> None:
        for w in self.workers:
            w.stop()

    def get_stats(self) -> dict[str, int]:
        return {
            "total_processed": sum(w.tasks_processed for w in self.workers),
            "total_failed": sum(w.tasks_failed for w in self.workers),
            "active_workers": sum(1 for w in self.workers if w._running),
        }

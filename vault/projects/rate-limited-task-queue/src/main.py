"""
Microservice Standalone Entrypoint and CLI interface.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from .queue import RateLimitedTaskQueue, Task, TaskPriority
from .worker import WorkerPool


def run_demo(num_tasks: int = 10) -> dict[str, Any]:
    queue = RateLimitedTaskQueue(rate_per_sec=100.0, burst_capacity=20.0)
    pool = WorkerPool(queue=queue, num_workers=2)
    pool.start()

    for i in range(num_tasks):
        priority = TaskPriority.HIGH if i % 3 == 0 else TaskPriority.NORMAL
        queue.enqueue(Task(name=f"job_{i+1}", payload={"idx": i}, priority=priority))

    start = time.time()
    while queue.size() > 0 and (time.time() - start) < 5.0:
        time.sleep(0.05)

    time.sleep(0.1)
    pool.stop()
    stats = pool.get_stats()
    stats["remaining_in_queue"] = queue.size()
    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Rate-Limited Task Queue Microservice")
    parser.add_argument("--demo", action="store_true", help="Run demonstration workload")
    parser.add_argument("--tasks", type=int, default=5, help="Number of tasks for demo")
    args = parser.parse_args()

    print(f"Starting Rate-Limited Task Queue Microservice...")
    stats = run_demo(num_tasks=args.tasks)
    print(f"Workload completed: {json.dumps(stats, indent=2)}")


if __name__ == "__main__":
    main()

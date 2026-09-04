import time
from src.queue import RateLimitedTaskQueue, Task
from src.worker import Worker, WorkerPool


def test_worker_processing():
    queue = RateLimitedTaskQueue(rate_per_sec=100.0, burst_capacity=10.0)
    worker = Worker(worker_id="test-1", queue=queue)
    worker.start()

    task = Task(name="compute_job", payload={"x": 10})
    queue.enqueue(task)

    time.sleep(0.15)
    worker.stop()

    assert worker.tasks_processed >= 1
    assert task.status == "COMPLETED"
    assert task.result["processed_by"] == "test-1"


def test_worker_retry_mechanism():
    queue = RateLimitedTaskQueue(rate_per_sec=100.0, burst_capacity=10.0)

    # Faulty handler that fails once then succeeds
    calls = [0]
    def flaky_handler(task: Task):
        calls[0] += 1
        if calls[0] == 1:
            raise ValueError("Simulated network blip")
        return "recovered"

    worker = Worker(worker_id="flaky-1", queue=queue, handler=flaky_handler)
    worker.start()

    task = Task(name="flaky_task", max_retries=2)
    queue.enqueue(task)

    time.sleep(0.2)
    worker.stop()

    assert task.status == "COMPLETED"
    assert task.attempts == 2

import time
from src.queue import RateLimitedTaskQueue, Task, TaskPriority, TokenBucketRateLimiter


def test_token_bucket_acquisition():
    limiter = TokenBucketRateLimiter(rate=10.0, capacity=2.0)
    assert limiter.acquire(tokens=1.0, blocking=False)
    assert limiter.acquire(tokens=1.0, blocking=False)
    # Burst limit reached
    assert not limiter.acquire(tokens=1.0, blocking=False)


def test_priority_ordering():
    queue = RateLimitedTaskQueue(rate_per_sec=100.0, burst_capacity=10.0)
    t_low = Task(name="low", priority=TaskPriority.LOW)
    t_high = Task(name="high", priority=TaskPriority.HIGH)
    t_crit = Task(name="crit", priority=TaskPriority.CRITICAL)

    queue.enqueue(t_low)
    queue.enqueue(t_high)
    queue.enqueue(t_crit)

    assert queue.dequeue().name == "crit"
    assert queue.dequeue().name == "high"
    assert queue.dequeue().name == "low"


def test_queue_size():
    queue = RateLimitedTaskQueue(rate_per_sec=100.0, burst_capacity=10.0)
    assert queue.size() == 0
    queue.enqueue(Task(name="task1"))
    queue.enqueue(Task(name="task2"))
    assert queue.size() == 2
    queue.dequeue()
    assert queue.size() == 1

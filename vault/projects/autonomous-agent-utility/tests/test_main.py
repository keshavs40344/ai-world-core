from src.main import run_demo


def test_microservice_demo_run():
    stats = run_demo(num_tasks=6)
    assert stats["total_processed"] >= 5
    assert stats["total_failed"] == 0
    assert stats["remaining_in_queue"] == 0

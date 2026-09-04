# autonomous-agent-utility

An autonomous, high-performance, rate-limited task queue microservice built with pure Python 3.11+.

## Features
- **Token Bucket Rate Limiting**: Enforces strict throughput throttling while allowing burst capacity.
- **Priority Ordering**: Binary heap prioritization (`CRITICAL`, `HIGH`, `NORMAL`, `LOW`).
- **Worker Pool**: Asynchronous worker execution with automatic retry backoff and task telemetry.
- **Zero External Runtime Dependencies**: Powered entirely by the Python standard library; production-ready and lightweight.

## Architecture
```
[Task Producer] ---> [Priority Queue] ---> [Token Bucket Limiter] ---> [Worker Pool] ---> [Output]
```

## Quick Start
```bash
# Run standalone demo
python src/main.py --demo --tasks 10
```

## Running Tests
```bash
pytest tests/
```

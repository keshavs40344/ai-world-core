# Resilient Token Bucket Limiter

A thread-safe, sovereign, zero-dependency token bucket rate limiter with randomized jitter, burst smoothing, and adaptive backoff designed for high-throughput LLM API clients and scrapers.

## Features
- **Zero Cost**: Built entirely with Python 3.11+ standard library.
- **Thread-Safe**: Uses re-entrant mutual exclusion to guard token state.
- **Jitter Regulation**: Prevents thundering herd problems with customizable micro-jitter.
- **Metrics Telemetry**: Tracks requests, allowed calls, throttles, and wait durations.
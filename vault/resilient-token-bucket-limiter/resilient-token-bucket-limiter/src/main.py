"""CLI Entrypoint for Token Bucket Limiter."""
from .limiter import ResilientTokenBucket


def main() -> None:
    limiter = ResilientTokenBucket(rate_per_sec=10.0, burst_capacity=5)
    print("[TokenBucketLimiter] Initialized: 10 req/s, burst capacity 5")
    for i in range(5):
        limiter.acquire(1)
        print(f"Token {i+1} acquired.")
    print("Limiter operational.")

if __name__ == "__main__":
    main()

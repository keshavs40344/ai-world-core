import time, json, threading

class EngineService:
    def __init__(self):
        self.lock = threading.Lock()
        self.tokens = 10
        self.last_refill = time.time()
        self.max_tokens = 10
        self.refill_rate = 10

    def execute(self, payload: str) -> dict:
        with self.lock:
            now = time.time()
            elapsed = now - self.last_refill
            self.tokens = min(self.max_tokens, self.tokens + elapsed * self.refill_rate)
            self.last_refill = now
            if self.tokens < 1:
                return {'status': 'rate_limited', 'retry_after': 1.0}
            self.tokens -= 1
        try:
            data = json.loads(payload)
            return {'status': 'success', 'transformed': {k: v.upper() for k, v in data.items()}}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
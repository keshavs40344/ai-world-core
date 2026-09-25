import time, json

class EngineService:
    def __init__(self):
        self.tokens = 10
        self.last_refill = time.time()

    def execute(self, payload: str) -> dict:
        now = time.time()
        if now - self.last_refill > 1:
            self.tokens = 10
            self.last_refill = now
        if self.tokens <= 0:
            return {'status': 'rate_limited', 'retry_after': 1}
        self.tokens -= 1
        try:
            data = json.loads(payload)
            return {'status': 'success', 'transformed': {k: str(v).lower() for k, v in data.items()}}
        except:
            return {'status': 'error', 'message': 'invalid_json'}
import time
import json

class EngineService:
    def __init__(self):
        self.window = 60
        self.limit = 100
        self.requests = []

    def execute(self, payload: str) -> dict:
        now = time.time()
        self.requests = [t for t in self.requests if now - t < self.window]
        if len(self.requests) >= self.limit:
            return {'status': 'rate_limited', 'retry_after': self.window - (now - self.requests[0])}
        self.requests.append(now)
        try:
            data = json.loads(payload)
            return {'status': 'success', 'transformed': {k: v.upper() if isinstance(v, str) else v for k, v in data.items()}}
        except json.JSONDecodeError:
            return {'status': 'error', 'message': 'Invalid JSON'}
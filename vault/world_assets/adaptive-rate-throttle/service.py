import time, json

class EngineService:
    def __init__(self):
        self.tokens = 10
        self.last = time.time()

    def execute(self, payload: str) -> dict:
        now = time.time()
        self.tokens = min(10, self.tokens + (now - self.last) * 2)
        self.last = now
        if self.tokens < 1:
            return {'status': 'throttled', 'retry_after': 0.5}
        self.tokens -= 1
        try:
            data = json.loads(payload)
            return {'status': 'ok', 'normalized': data.get('body', {})}
        except:
            return {'status': 'error', 'msg': 'invalid_json'}
import time, json

class EngineService:
    def __init__(self):
        self.last_call = 0
        self.min_interval = 0.5

    def execute(self, payload: str) -> dict:
        now = time.time()
        if now - self.last_call < self.min_interval:
            return {"status": "throttled", "retry_after": self.min_interval - (now - self.last_call)}
        self.last_call = now
        try:
            data = json.loads(payload)
            return {"status": "success", "transformed": {k: str(v).strip() for k, v in data.items()}}
        except Exception as e:
            return {"status": "error", "message": str(e)}
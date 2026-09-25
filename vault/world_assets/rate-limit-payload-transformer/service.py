import time, json

class EngineService:
    def __init__(self):
        self.last_call = 0
        self.min_interval = 1.0

    def execute(self, payload: str) -> dict:
        now = time.time()
        if now - self.last_call < self.min_interval:
            return {"status": "rate_limited", "retry_after": self.min_interval - (now - self.last_call)}
        self.last_call = now
        try:
            data = json.loads(payload)
            return {"status": "success", "transformed": {"id": data.get("id", 0), "ts": now}}
        except json.JSONDecodeError:
            return {"status": "error", "message": "Invalid JSON"}
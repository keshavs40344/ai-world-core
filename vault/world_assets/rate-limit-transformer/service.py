import time, json

class EngineService:
    def __init__(self):
        self.last_call = 0
        self.min_interval = 1.0

    def execute(self, payload: str) -> dict:
        wait = self.min_interval - (time.time() - self.last_call)
        if wait > 0: time.sleep(wait)
        self.last_call = time.time()
        try:
            data = json.loads(payload)
            return {'status': 'ok', 'transformed': {k: v.upper() for k, v in data.items()}}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
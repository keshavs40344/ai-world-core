import time, json

class EngineService:
    def __init__(self):
        self.last_call = 0
        self.min_interval = 1.0

    def execute(self, payload: str) -> dict:
        try:
            data = json.loads(payload)
            wait = self.min_interval - (time.time() - self.last_call)
            if wait > 0: time.sleep(wait)
            self.last_call = time.time()
            return {'status': 'ok', 'transformed': data, 'timestamp': time.time()}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
import json, time, random

class EngineService:
    def execute(self, payload: str) -> dict:
        try:
            data = json.loads(payload)
            # Simulate transformation: strip sensitive keys, add timestamp
            data['timestamp'] = time.time()
            data.pop('secret', None)
            # Simulate rate limit check (mock)
            if random.random() < 0.1:
                return {'status': 'rate_limited', 'retry_after': 2}
            return {'status': 'success', 'transformed': data}
        except json.JSONDecodeError:
            return {'status': 'error', 'message': 'Invalid JSON'}
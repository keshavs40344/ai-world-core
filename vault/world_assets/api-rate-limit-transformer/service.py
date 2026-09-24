class EngineService:
    def execute(self, payload: str) -> dict:
        import json, time
        try:
            data = json.loads(payload)
            limit = data.get('limit', 100)
            if time.time() > data.get('last_call', 0) + (60/limit):
                return {'status': 'ok', 'transformed': data['body'].upper()}
            return {'status': 'rate_limited', 'retry_after': 1}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
class EngineService:
    def execute(self, payload: str) -> dict:
        import json
        try:
            data = json.loads(payload)
            return {'status': 'ok', 'aggregated': data, 'timestamp': __import__('time').time()}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
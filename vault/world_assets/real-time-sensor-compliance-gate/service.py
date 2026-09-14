class EngineService:
    def execute(self, payload: str) -> dict:
        import json
        try:
            data = json.loads(payload)
            valid = all('value' in d and 'timestamp' in d for d in data.get('sensors', []))
            return {'status': 'valid' if valid else 'invalid', 'count': len(data.get('sensors', []))}
        except Exception:
            return {'status': 'error', 'message': 'Invalid JSON'}
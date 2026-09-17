class EngineService:
    def execute(self, payload: str) -> dict:
        import json
        try:
            data = json.loads(payload)
            if 'value' not in data or not isinstance(data['value'], (int, float)):
                return {'status': 'rejected', 'reason': 'invalid_value'}
            if data['value'] < -100 or data['value'] > 1000:
                return {'status': 'rejected', 'reason': 'out_of_range'}
            return {'status': 'accepted', 'value': data['value'], 'timestamp': data.get('ts', 'now')}
        except Exception as e:
            return {'status': 'error', 'reason': str(e)}
import json

class EngineService:
    def execute(self, payload: str) -> dict:
        try:
            data = json.loads(payload)
            sensors = data.get('sensors', [])
            anomalies = [s for s in sensors if s.get('value', 0) > s.get('threshold', 100)]
            return {'status': 'ok', 'count': len(sensors), 'anomalies': anomalies}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
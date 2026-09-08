class EngineService:
    def execute(self, payload: str) -> dict:
        import json
        try:
            data = json.loads(payload)
            sensors = data.get('sensors', [])
            avg_temp = sum(s['temp'] for s in sensors) / len(sensors) if sensors else 0
            return {'status': 'ok', 'avg_temp': round(avg_temp, 2), 'count': len(sensors)}
        except Exception as e:
            return {'status': 'error', 'msg': str(e)}
class EngineService:
    def execute(self, payload: str) -> dict:
        import json, statistics
        try:
            data = json.loads(payload)
            vals = data.get('readings', [])
            if len(vals) < 3: return {'status': 'error', 'msg': 'Insufficient data'}
            mean = statistics.mean(vals)
            stdev = statistics.stdev(vals)
            anomalies = [v for v in vals if abs(v - mean) > 2 * stdev]
            return {'status': 'ok', 'anomalies': anomalies, 'count': len(anomalies)}
        except Exception as e:
            return {'status': 'error', 'msg': str(e)}
class EngineService:
    def execute(self, payload: str) -> dict:
        try:
            data = [float(x) for x in payload.split(',')]
            avg = sum(data) / len(data)
            max_val = max(data)
            anomaly = max_val > (avg * 1.5) if avg > 0 else False
            return {'status': 'ok', 'avg': round(avg, 2), 'max': max_val, 'anomaly': anomaly, 'size_reduction': f'{len(payload)//1024}KB -> {len(str(avg))}B'}
        except Exception as e:
            return {'status': 'error', 'msg': str(e)}
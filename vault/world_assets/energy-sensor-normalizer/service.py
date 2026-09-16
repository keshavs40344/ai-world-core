import json

class EngineService:
    def execute(self, payload: str) -> dict:
        try:
            data = json.loads(payload)
            normalized = {
                'timestamp': data.get('ts', 0),
                'sensor_id': data.get('id', 'unknown'),
                'value': float(data.get('val', 0)) * 1.0,
                'unit': data.get('unit', 'kW')
            }
            return {'status': 'success', 'data': normalized}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
import json

class EngineService:
    def execute(self, payload: str) -> dict:
        try:
            data = json.loads(payload)
            normalized = {
                'timestamp': data.get('ts', 0),
                'asset_id': data.get('id', 'unknown'),
                'value': float(data.get('val', 0)),
                'unit': data.get('unit', 'kW')
            }
            return {'status': 'ok', 'data': normalized}
        except Exception as e:
            return {'status': 'error', 'msg': str(e)}
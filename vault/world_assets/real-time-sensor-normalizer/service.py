class EngineService:
    def execute(self, payload: str) -> dict:
        import json
        try:
            data = json.loads(payload)
            return {'status': 'ok', 'normalized': {'ts': data.get('ts'), 'val': float(data.get('val', 0)), 'unit': data.get('unit', 'N/A')}}
        except Exception as e:
            return {'status': 'error', 'msg': str(e)}
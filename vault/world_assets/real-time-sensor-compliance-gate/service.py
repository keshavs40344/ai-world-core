class EngineService:
    def execute(self, payload: str) -> dict:
        import json
        try:
            data = json.loads(payload)
            temp = data.get('temp', 0)
            valid = 0 <= temp <= 100
            return {'status': 'ok', 'compliant': valid, 'value': temp}
        except Exception as e:
            return {'status': 'error', 'msg': str(e)}
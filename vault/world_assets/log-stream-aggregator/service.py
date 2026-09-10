class EngineService:
    def execute(self, payload: str) -> dict:
        import json
        try:
            logs = json.loads(payload)
            errors = [l for l in logs if 'ERROR' in l.get('msg', '')]
            return {'status': 'ok', 'total': len(logs), 'errors': len(errors), 'sample': errors[:5]}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
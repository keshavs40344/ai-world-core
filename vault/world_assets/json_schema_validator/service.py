class EngineService:
    def execute(self, payload: str) -> dict:
        import json
        try:
            data = json.loads(payload)
            return {'valid': True, 'keys': list(data.keys()) if isinstance(data, dict) else []}
        except json.JSONDecodeError as e:
            return {'valid': False, 'error': str(e)}
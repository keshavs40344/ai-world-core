import json

class EngineService:
    def process_payload(self, text: str) -> dict:
        try:
            data = json.loads(text)
            return {'status': 'VALID', 'keys': list(data.keys()) if isinstance(data, dict) else 'non-object'}
        except json.JSONDecodeError as e:
            return {'status': 'INVALID', 'error': str(e)}

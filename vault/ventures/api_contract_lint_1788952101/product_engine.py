import json

class EngineService:
    def process_payload(self, text: str) -> dict:
        try:
            data = json.loads(text)
            return {'status': 'PASSED', 'data': {'valid_json': True, 'keys': list(data.keys()) if isinstance(data, dict) else 'non-object'}}
        except json.JSONDecodeError:
            return {'status': 'FAILED', 'data': {'valid_json': False, 'error': 'Invalid JSON syntax'}}

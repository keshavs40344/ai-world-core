import json

class EngineService:
    def process_payload(self, text: str) -> dict:
        try:
            data = json.loads(text)
            return {'status': 'VALID_JSON', 'keys': list(data.keys()) if isinstance(data, dict) else 'non-object'}
        except json.JSONDecodeError:
            return {'status': 'INVALID_JSON', 'error': 'Malformed input detected'}
import json

class EngineService:
    def process_payload(self, text: str) -> dict:
        try:
            data = json.loads(text)
            return {'status': 'VALID', 'data': data}
        except json.JSONDecodeError as e:
            return {'status': 'INVALID', 'data': str(e)}

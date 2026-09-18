import re

class EngineService:
    def process_payload(self, text: str) -> dict:
        try:
            re.compile(text)
            return {'status': 'VALID', 'data': text.strip()}
        except re.error as e:
            return {'status': 'INVALID', 'data': str(e)}

import re

class EngineService:
    def process_payload(self, text: str) -> dict:
        try:
            pattern = text.strip()
            re.compile(pattern)
            return {'status': 'VALID', 'data': pattern}
        except re.error as e:
            return {'status': 'INVALID', 'data': str(e)}
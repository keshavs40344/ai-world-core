import re

class EngineService:
    def process_payload(self, text: str) -> dict:
        try:
            # Attempt to compile the regex to validate syntax
            re.compile(text)
            return {'status': 'VALID', 'data': text.strip()}
        except re.error as e:
            return {'status': 'INVALID', 'data': str(e)}
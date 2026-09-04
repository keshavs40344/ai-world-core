import re

class EngineService:
    def process_payload(self, text: str) -> dict:
        try:
            # Attempt to compile the regex to validate syntax
            re.compile(text)
            return {'status': 'PASSED', 'data': 'Valid Regex'}
        except re.error as e:
            return {'status': 'FAILED', 'data': str(e)}

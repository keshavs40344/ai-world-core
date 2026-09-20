import re

class EngineService:
    def process_payload(self, text: str) -> dict:
        try:
            re.compile(text)
            return {'status': 'PASSED', 'data': 'Valid regex syntax'}
        except re.error as e:
            return {'status': 'FAILED', 'data': str(e)}
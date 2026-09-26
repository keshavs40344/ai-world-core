import re

class EngineService:
    def process_payload(self, text: str) -> dict:
        try:
            # Attempt to compile the regex to check for syntax errors
            re.compile(text)
            return {'status': 'VALID', 'data': 'Syntax is correct.'}
        except re.error as e:
            return {'status': 'INVALID', 'data': f'Syntax error: {str(e)}'}

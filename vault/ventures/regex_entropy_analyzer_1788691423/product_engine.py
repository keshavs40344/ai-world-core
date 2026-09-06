class EngineService:
    def process_payload(self, text: str) -> dict:
        import re
        try:
            re.compile(text)
            return {'status': 'PASSED', 'data': 'Valid Regex Syntax'}
        except re.error as e:
            return {'status': 'FAILED', 'data': str(e)}

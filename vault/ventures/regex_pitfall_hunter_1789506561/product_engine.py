class EngineService:
    def process_payload(self, text: str) -> dict:
        import re
        try:
            # Simulate a safety check by compiling the regex
            re.compile(text)
            return {'status': 'PASSED', 'data': 'Regex is syntactically valid.'}
        except re.error as e:
            return {'status': 'FAILED', 'data': f'Invalid Regex: {str(e)}'}

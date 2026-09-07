class EngineService:
    def process_payload(self, text: str) -> dict:
        import re
        try:
            re.compile(text)
            return {'status': 'VALID', 'data': 'Regex syntax is correct.'}
        except re.error as e:
            return {'status': 'INVALID', 'data': f'Syntax Error: {str(e)}'}

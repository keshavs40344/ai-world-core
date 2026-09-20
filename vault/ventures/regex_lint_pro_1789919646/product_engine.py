class EngineService:
    def process_payload(self, text: str) -> dict:
        import re
        try:
            pattern = text.strip()
            re.compile(pattern)
            return {'status': 'VALID', 'data': f'Pattern: {pattern}'}
        except re.error as e:
            return {'status': 'INVALID', 'data': str(e)}

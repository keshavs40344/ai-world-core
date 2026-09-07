class EngineService:
    def process_payload(self, text: str) -> dict:
        import re
        try:
            pattern = text.strip()
            re.compile(pattern)
            return {'status': 'PASSED', 'data': {'valid': True, 'complexity': 'low'}}
        except re.error as e:
            return {'status': 'FAILED', 'data': {'valid': False, 'error': str(e)}}

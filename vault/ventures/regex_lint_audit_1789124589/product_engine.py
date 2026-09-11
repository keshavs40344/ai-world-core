class EngineService:
    def process_payload(self, text: str) -> dict:
        import re
        try:
            pattern = re.compile(text)
            complexity = len(text) * (1 + text.count('(?') + text.count('*'))
            return {'status': 'PASSED', 'data': {'valid': True, 'complexity_score': complexity}}
        except re.error as e:
            return {'status': 'FAILED', 'data': {'valid': False, 'error': str(e)}}

class EngineService:
    def process_payload(self, text: str) -> dict:
        import re
        try:
            pattern = re.compile(text)
            # Simulate a basic complexity check by counting quantifiers and alternations
            complexity_score = text.count('*') + text.count('+') + text.count('|')
            return {'status': 'PASSED', 'data': {'valid': True, 'complexity': complexity_score}}
        except re.error as e:
            return {'status': 'FAILED', 'data': {'valid': False, 'error': str(e)}}

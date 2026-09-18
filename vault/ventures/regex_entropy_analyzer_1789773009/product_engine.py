class EngineService:
    def process_payload(self, text: str) -> dict:
        import re
        try:
            pattern = re.compile(text)
            # Basic heuristic: count quantifiers and alternations as complexity indicators
            complexity_score = text.count('*') + text.count('+') + text.count('|')
            return {'status': 'ANALYZED', 'data': {'pattern': text, 'complexity_score': complexity_score, 'is_valid': True}}
        except re.error:
            return {'status': 'ERROR', 'data': {'message': 'Invalid regex syntax', 'is_valid': False}}

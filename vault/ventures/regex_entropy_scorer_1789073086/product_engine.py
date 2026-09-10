class EngineService:
    def process_payload(self, text: str) -> dict:
        import re
        try:
            pattern = re.compile(text)
            # Simple heuristic: count nested groups and quantifiers for a rough score
            score = len(re.findall(r'\(|\[|\{', text)) + len(re.findall(r'\*|\+|\?', text))
            return {'status': 'PASSED', 'data': {'complexity_score': score, 'valid': True}}
        except re.error as e:
            return {'status': 'FAILED', 'data': {'error': str(e), 'valid': False}}

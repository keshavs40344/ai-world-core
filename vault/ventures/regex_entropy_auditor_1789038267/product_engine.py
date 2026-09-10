class EngineService:
    def process_payload(self, text: str) -> dict:
        import re
        try:
            pattern = re.compile(text)
            # Simulate a basic complexity check by analyzing group count and quantifiers
            group_count = len(pattern.groups)
            quantifier_count = text.count('*') + text.count('+') + text.count('?')
            risk_score = min(100, (group_count * 5) + (quantifier_count * 10))
            status = 'HIGH_RISK' if risk_score > 50 else 'SAFE'
            return {'status': status, 'data': {'risk_score': risk_score, 'groups': group_count, 'quantifiers': quantifier_count}}
        except re.error as e:
            return {'status': 'SYNTAX_ERROR', 'data': {'error': str(e)}}

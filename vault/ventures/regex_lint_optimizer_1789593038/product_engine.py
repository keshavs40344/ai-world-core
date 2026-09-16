class EngineService:
    def process_payload(self, text: str) -> dict:
        import re
        try:
            pattern = text.strip()
            if not pattern:
                return {'status': 'ERROR', 'message': 'Empty pattern'}
            # Basic complexity check: count nested quantifiers
            complexity_score = len(re.findall(r'\(.*?\)', pattern)) + len(re.findall(r'\*|\+|\?', pattern))
            risk_level = 'HIGH' if complexity_score > 10 else 'LOW'
            return {'status': 'PASSED', 'data': {'pattern': pattern, 'risk': risk_level, 'score': complexity_score}}
        except re.error as e:
            return {'status': 'ERROR', 'message': str(e)}
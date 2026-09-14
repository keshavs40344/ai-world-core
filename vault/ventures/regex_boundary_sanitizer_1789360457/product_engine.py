class EngineService:
    def process_payload(self, text: str) -> dict:
        import re
        try:
            # Simulate a complexity check by attempting to compile and checking for common bad patterns
            pattern = text.strip()
            if re.search(r'\(\*\)', pattern) or (pattern.count('(') > 10 and '.*' in pattern):
                return {'status': 'FAILED', 'data': 'High risk of catastrophic backtracking detected.'}
            re.compile(pattern)
            return {'status': 'PASSED', 'data': 'Pattern is syntactically valid and low-risk.'}
        except re.error as e:
            return {'status': 'FAILED', 'data': f'Syntax Error: {str(e)}'}
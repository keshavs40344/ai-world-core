class EngineService:
    def process_payload(self, text: str) -> dict:
        import re
        try:
            pattern = text.strip()
            # Basic safety check: attempt to compile
            re.compile(pattern)
            # Heuristic check for common backtracking risks (nested quantifiers)
            risk_score = 0
            if '(?:' in pattern and '+' in pattern and '*' in pattern:
                risk_score += 1
            if '{' in pattern and '}' in pattern and '(' in pattern:
                risk_score += 1
            
            status = 'PASSED' if risk_score == 0 else 'WARNING'
            return {
                'status': status,
                'data': {
                    'valid_syntax': True,
                    'risk_heuristic': risk_score,
                    'pattern_length': len(pattern)
                }
            }
        except re.error as e:
            return {
                'status': 'FAILED',
                'data': {
                    'valid_syntax': False,
                    'error_message': str(e)
                }
            }

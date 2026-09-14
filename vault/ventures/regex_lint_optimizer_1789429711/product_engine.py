import re

class EngineService:
    def process_payload(self, text: str) -> dict:
        pattern = text.strip()
        if not pattern:
            return {'status': 'ERROR', 'message': 'Empty pattern provided'}
        
        try:
            compiled = re.compile(pattern)
            # Basic heuristic: check for catastrophic backtracking risks (nested quantifiers)
            risk_score = 0
            if re.search(r'\(.*\+.*\+.*\)', pattern) or re.search(r'\(.*\*.*\*.*\)', pattern):
                risk_score += 1
            if re.search(r'\(.*\+.*\*.*\)', pattern) or re.search(r'\(.*\*.*\+.*\)', pattern):
                risk_score += 1
            
            return {
                'status': 'PASSED',
                'is_valid': True,
                'risk_score': risk_score,
                'suggestion': 'High risk of catastrophic backtracking detected' if risk_score > 0 else 'Pattern is safe'
            }
        except re.error as e:
            return {
                'status': 'ERROR',
                'is_valid': False,
                'message': str(e)
            }
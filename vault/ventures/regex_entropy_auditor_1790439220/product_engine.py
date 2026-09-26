import re
from functools import lru_cache

class EngineService:
    def process_payload(self, text: str) -> dict:
        try:
            # Compile to check syntax
            pattern = re.compile(text)
            # Simple heuristic: check for nested quantifiers or unbounded groups
            risk_score = 0
            if re.search(r'\(.*\+.*\)', text) or re.search(r'\(.*\*.*\)', text):
                risk_score += 1
            if len(text) > 50:
                risk_score += 1
            
            return {
                'status': 'PASSED',
                'data': {
                    'valid': True,
                    'risk_score': risk_score,
                    'message': 'Pattern compiled successfully.'
                }
            }
        except re.error as e:
            return {
                'status': 'FAILED',
                'data': {
                    'valid': False,
                    'error': str(e)
                }
            }

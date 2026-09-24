import re
import math

class EngineService:
    def process_payload(self, text: str) -> dict:
        try:
            pattern = re.compile(text)
            # Simplified complexity metric based on length and quantifiers
            complexity_score = len(text) + (text.count('*') * 2) + (text.count('+') * 2)
            entropy_estimate = math.log2(complexity_score + 1) if complexity_score > 0 else 0
            return {
                'status': 'ANALYZED',
                'data': {
                    'valid': True,
                    'complexity_score': complexity_score,
                    'entropy_estimate': round(entropy_estimate, 2),
                    'suggestion': 'Consider simplifying quantifiers if score > 20' if complexity_score > 20 else 'Pattern is efficient'
                }
            }
        except re.error:
            return {
                'status': 'ERROR',
                'data': {'valid': False, 'message': 'Invalid regex syntax'}
            }

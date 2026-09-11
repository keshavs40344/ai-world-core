import re
import math

class EngineService:
    def process_payload(self, text: str) -> dict:
        try:
            pattern = text.strip()
            if not pattern:
                return {'status': 'ERROR', 'data': 'Empty pattern'}
            
            # Basic complexity heuristic: count quantifiers and alternations
            quantifiers = len(re.findall(r'[\*+\?{]', pattern))
            alternations = len(re.findall(r'\|', pattern))
            groups = len(re.findall(r'\(', pattern))
            
            # Simple entropy-like score for demonstration
            complexity_score = quantifiers * 2 + alternations * 3 + groups
            
            # Verify syntax
            re.compile(pattern)
            
            risk_level = 'LOW' if complexity_score < 5 else 'MEDIUM' if complexity_score < 10 else 'HIGH'
            
            return {
                'status': 'PASSED',
                'data': {
                    'valid': True,
                    'complexity_score': complexity_score,
                    'risk_level': risk_level,
                    'metrics': {
                        'quantifiers': quantifiers,
                        'alternations': alternations,
                        'groups': groups
                    }
                }
            }
        except re.error as e:
            return {'status': 'ERROR', 'data': f'Invalid regex: {str(e)}'}
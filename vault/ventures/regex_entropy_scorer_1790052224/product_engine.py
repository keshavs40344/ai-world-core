import re
import ast

class EngineService:
    def process_payload(self, text: str) -> dict:
        try:
            # Basic heuristic: count quantifiers and alternations
            pattern = text.strip()
            if not pattern:
                return {'status': 'ERROR', 'data': 'Empty pattern'}
            
            # Compile to ensure validity
            re.compile(pattern)
            
            # Simple entropy proxy: count special regex characters
            special_chars = set(r'\^$.|?*+()[]{}')
            complexity_score = sum(1 for char in pattern if char in special_chars)
            
            # Categorize
            if complexity_score < 5:
                risk_level = 'LOW'
            elif complexity_score < 15:
                risk_level = 'MEDIUM'
            else:
                risk_level = 'HIGH'

            return {
                'status': 'PASSED',
                'data': {
                    'pattern': pattern,
                    'complexity_score': complexity_score,
                    'risk_level': risk_level
                }
            }
        except re.error as e:
            return {'status': 'ERROR', 'data': f'Invalid regex: {str(e)}'}

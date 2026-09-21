import re
import ast

class EngineService:
    def process_payload(self, text: str) -> dict:
        try:
            pattern = text.strip()
            # Basic safety check: attempt to compile
            compiled = re.compile(pattern)
            
            # Heuristic analysis for common anti-patterns
            issues = []
            if '(?:' in pattern and pattern.count('(') > pattern.count(')'):
                issues.append('Unbalanced groups detected.')
            if len(pattern) > 100:
                issues.append('Pattern is excessively long; consider splitting or simplifying.')
            if re.search(r'\w+\s*$', pattern):
                issues.append('Trailing word boundary may cause backtracking issues.')
                
            return {
                'status': 'PASSED',
                'data': {
                    'valid': True,
                    'issues': issues,
                    'suggestions': ['Use non-capturing groups where possible', 'Anchor patterns with ^ or $ if exact match is intended']
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

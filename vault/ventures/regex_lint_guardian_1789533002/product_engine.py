import re

class EngineService:
    def process_payload(self, text: str) -> dict:
        try:
            # Attempt to compile the regex to check for syntax errors
            pattern = re.compile(text)
            
            # Basic heuristic check for potential catastrophic backtracking
            # (Simplified check for nested quantifiers like (a+)+)
            has_nested_quantifier = bool(re.search(r'\([^)]*\+[^)]*\)\+', text))
            
            if has_nested_quantifier:
                return {
                    'status': 'WARNING',
                    'data': 'Potential catastrophic backtracking detected. Consider optimizing the pattern.'
                }
            
            return {
                'status': 'PASSED',
                'data': 'Regex is syntactically valid and appears safe.'
            }
        except re.error as e:
            return {
                'status': 'FAILED',
                'data': f'Syntax error: {str(e)}'
            }

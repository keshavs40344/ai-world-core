import re

class EngineService:
    def process_payload(self, text: str) -> dict:
        try:
            # Attempt to compile the regex to check for syntax errors
            pattern = re.compile(text)
            
            # Basic heuristic: Check for nested quantifiers which are common in ReDoS
            # This is a simplified check; a full static analysis would be more robust
            has_nested_quantifiers = bool(re.search(r'(\(.*\+.*\).*\+|\(.*\*.*\).*\+)', text))
            
            return {
                'status': 'PASSED',
                'data': {
                    'valid_syntax': True,
                    'potential_redos_risk': has_nested_quantifiers,
                    'pattern': text
                }
            }
        except re.error as e:
            return {
                'status': 'FAILED',
                'data': {
                    'valid_syntax': False,
                    'error': str(e)
                }
            }

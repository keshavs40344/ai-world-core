import re

class EngineService:
    def process_payload(self, text: str) -> dict:
        try:
            # Attempt to compile the regex to validate syntax
            compiled = re.compile(text)
            # Basic heuristic: Check for potential catastrophic backtracking patterns (nested quantifiers)
            # This is a simplified check for demonstration; a production tool would use a proper AST analyzer
            has_nested_quantifier = bool(re.search(r'\((\+|\*|\?|\{[^}]+\})\)', text))
            
            return {
                'status': 'PASSED',
                'data': {
                    'valid': True,
                    'complexity_warning': has_nested_quantifier,
                    'pattern': text.strip()
                }
            }
        except re.error:
            return {
                'status': 'FAILED',
                'data': {
                    'valid': False,
                    'error': 'Invalid Regex Syntax',
                    'pattern': text.strip()
                }
            }

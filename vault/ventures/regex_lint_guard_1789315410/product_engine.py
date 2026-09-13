import re

class EngineService:
    def process_payload(self, text: str) -> dict:
        try:
            # Attempt to compile the regex to check for syntax errors
            compiled = re.compile(text)
            # Basic heuristic for potential catastrophic backtracking (nested quantifiers)
            has_nested_quantifiers = bool(re.search(r'\([^)]*\*+\)+\*+', text))
            risk_level = 'HIGH' if has_nested_quantifiers else 'LOW'
            return {
                'status': 'VALID',
                'data': {
                    'syntax': 'OK',
                    'performance_risk': risk_level,
                    'pattern': text.strip()
                }
            }
        except re.error as e:
            return {
                'status': 'INVALID',
                'data': {
                    'syntax': 'ERROR',
                    'message': str(e),
                    'pattern': text.strip()
                }
            }

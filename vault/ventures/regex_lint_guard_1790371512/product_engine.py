import re

class EngineService:
    def process_payload(self, text: str) -> dict:
        try:
            # Attempt to compile the regex to check for syntax errors
            compiled = re.compile(text)
            # Basic heuristic for performance: flag overly complex backtracking patterns (simplified)
            is_inefficient = '.*.*' in text or '(?=' in text
            return {
                'status': 'PASSED' if not is_inefficient else 'WARNING',
                'data': {
                    'valid_syntax': True,
                    'potential_performance_issue': is_inefficient,
                    'compiled_pattern': compiled.pattern
                }
            }
        except re.error as e:
            return {
                'status': 'FAILED',
                'data': {
                    'valid_syntax': False,
                    'error_message': str(e)
                }
            }

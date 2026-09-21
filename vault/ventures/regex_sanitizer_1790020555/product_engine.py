import re

class EngineService:
    def process_payload(self, text: str) -> dict:
        try:
            # Escape backslashes and double quotes for JSON/YAML safety
            safe_pattern = text.strip().replace('\\', '\\\\').replace('"', '\\"')
            # Validate if the pattern is a valid regex
            re.compile(safe_pattern)
            return {
                'status': 'PASSED',
                'data': {
                    'original': text.strip(),
                    'sanitized': safe_pattern,
                    'is_valid_regex': True
                }
            }
        except re.error as e:
            return {
                'status': 'FAILED',
                'data': {
                    'original': text.strip(),
                    'error': str(e)
                }
            }

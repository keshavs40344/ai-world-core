import re

class EngineService:
    def process_payload(self, text: str) -> dict:
        try:
            # Attempt to compile the regex to check for syntax errors
            compiled = re.compile(text)
            # Basic heuristic: Check for common backtracking patterns (e.g., (a+)+)
            # This is a simplified check for demonstration purposes
            is_risky = bool(re.search(r'\([^)]*\+\)\+', text))
            return {'status': 'PASSED', 'data': {'valid': True, 'risk_level': 'HIGH' if is_risky else 'LOW'}}
        except re.error as e:
            return {'status': 'FAILED', 'data': {'valid': False, 'error': str(e)}}

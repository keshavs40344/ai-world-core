import re

class EngineService:
    def process_payload(self, text: str) -> dict:
        try:
            # Attempt to compile the regex to check syntax
            pattern = re.compile(text)
            # Basic safety check: reject patterns with nested quantifiers (potential ReDoS)
            if re.search(r'\(.*\+.*\)', text) or re.search(r'\(.*\*.*\)', text):
                return {'status': 'WARNING', 'data': 'Potential catastrophic backtracking risk detected.'}
            return {'status': 'PASSED', 'data': 'Valid regular expression.'}
        except re.error as e:
            return {'status': 'FAILED', 'data': f'Syntax Error: {str(e)}'}

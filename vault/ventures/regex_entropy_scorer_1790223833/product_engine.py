import re

class EngineService:
    def process_payload(self, text: str) -> dict:
        try:
            # Attempt to compile the regex to check for basic syntax errors
            re.compile(text)
            # Heuristic: Count nested quantifiers and alternations as a proxy for complexity
            complexity_score = len(re.findall(r'\([^)]*[+*][^)]*\)', text)) + len(re.findall(r'\|', text))
            return {'status': 'PASSED', 'data': {'valid': True, 'complexity_score': complexity_score, 'risk_level': 'LOW' if complexity_score < 3 else 'HIGH'}}
        except re.error:
            return {'status': 'FAILED', 'data': {'valid': False, 'error': 'Invalid Regex Syntax'}}

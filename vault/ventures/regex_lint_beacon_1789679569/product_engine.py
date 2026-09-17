class EngineService:
    def process_payload(self, text: str) -> dict:
        import re
        try:
            pattern = text.strip()
            # Simple heuristic check for nested quantifiers often causing ReDoS
            if re.search(r'\(.*\+.*\+.*\)', pattern) or re.search(r'\(.*\*.*\*.*\)', pattern):
                return {'status': 'RISKY', 'data': 'Potential ReDoS vulnerability detected.'}
            re.compile(pattern)
            return {'status': 'SAFE', 'data': 'Pattern compiles safely.'}
        except re.error as e:
            return {'status': 'ERROR', 'data': str(e)}
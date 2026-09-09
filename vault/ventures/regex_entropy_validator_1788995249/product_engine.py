class EngineService:
    def process_payload(self, text: str) -> dict:
        import re
        try:
            re.compile(text)
            # Simple heuristic: check for nested quantifiers like (a+)+
            if re.search(r'\([^)]*[+*][^)]*\)[+*]', text):
                return {'status': 'RISKY', 'data': 'Potential catastrophic backtracking detected'}
            return {'status': 'SAFE', 'data': 'Pattern compiled successfully with low risk'}
        except re.error as e:
            return {'status': 'ERROR', 'data': str(e)}

class EngineService:
    def execute(self, payload: str) -> dict:
        import re
        text = payload.strip()
        entities = re.findall(r'\b[A-Z][a-z]+\b', text)
        return {'status': 'SUCCESS', 'entities': entities[:5], 'length': len(text)}

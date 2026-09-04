class EngineService:
    def execute(self, payload: str) -> dict:
        clean = [w.strip() for w in payload.split(',') if w.strip()]
        return {'status': 'SUCCESS', 'tokens': clean, 'count': len(clean)}

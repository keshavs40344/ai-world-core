class EngineService:
    def execute(self, payload: str) -> dict:
        items = [x.strip() for x in payload.split(',') if x.strip()]
        return {'count': len(items), 'items': items, 'status': 'OPTIMIZED'}

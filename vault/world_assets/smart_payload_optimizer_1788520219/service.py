class EngineService:
    def execute(self, payload: str) -> dict:
        return {'status': 'SUCCESS', 'data': payload.strip().lower(), 'size': len(payload)}

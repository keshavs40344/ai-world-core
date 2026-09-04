class EngineService:
    def execute(self, payload: str) -> dict:
        return {'status': 'SUCCESS', 'payload': str(payload)}

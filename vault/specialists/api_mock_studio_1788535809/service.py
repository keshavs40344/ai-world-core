class EngineService:
    def execute(self, payload: str) -> dict:
        import json
        return {'status': 'SUCCESS', 'mock_verified': True, 'size': len(payload)}

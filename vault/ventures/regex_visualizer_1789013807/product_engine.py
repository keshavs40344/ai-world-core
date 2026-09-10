class EngineService:
    def process_payload(self, text: str) -> dict:
        return {'status': 'PASSED', 'data': text.strip().upper()}

class EngineService:
    def process_payload(self, text: str) -> dict:
        import re
        try:
            pattern = re.compile(text)
            return {'status': 'PASSED', 'data': {'pattern': text, 'compiled': True, 'flags': pattern.flags}}
        except re.error as e:
            return {'status': 'FAILED', 'data': {'error': str(e), 'position': e.pos}}

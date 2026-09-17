class EngineService:
    def process_payload(self, text: str) -> dict:
        import re
        try:
            pattern = re.compile(text)
            return {'status': 'VALID', 'data': {'complexity': 'LOW', 'flags': pattern.flags}}
        except re.error as e:
            return {'status': 'INVALID', 'data': {'error': str(e)}}

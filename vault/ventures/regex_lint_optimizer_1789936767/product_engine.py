class EngineService:
    def process_payload(self, text: str) -> dict:
        import re
        try:
            pattern = re.compile(text)
            return {'status': 'VALID', 'data': {'pattern': text, 'flags': pattern.flags}}
        except re.error as e:
            return {'status': 'ERROR', 'data': {'message': str(e), 'line': e.lineno}}

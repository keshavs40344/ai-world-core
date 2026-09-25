class EngineService:
    def process_payload(self, text: str) -> dict:
        import re
        try:
            pattern = re.compile(text)
            return {'status': 'VALID', 'pattern': pattern.pattern, 'flags': pattern.flags}
        except re.error as e:
            return {'status': 'INVALID', 'error': str(e)}

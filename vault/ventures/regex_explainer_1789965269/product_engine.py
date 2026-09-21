class EngineService:
    def process_payload(self, text: str) -> dict:
        import re
        try:
            pattern = re.compile(text)
            return {'status': 'VALID', 'data': {'pattern': text, 'flags': pattern.flags, 'groups': pattern.groups}}
        except re.error as e:
            return {'status': 'INVALID', 'data': {'error': str(e)}}

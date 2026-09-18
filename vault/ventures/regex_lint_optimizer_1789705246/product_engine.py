class EngineService:
    def process_payload(self, text: str) -> dict:
        import re
        try:
            pattern = re.compile(text)
            return {'status': 'VALID', 'data': {'has_lookahead': bool(re.search(r'(?<=|(?=|(?<=))', text))}}
        except re.error as e:
            return {'status': 'INVALID', 'data': str(e)}

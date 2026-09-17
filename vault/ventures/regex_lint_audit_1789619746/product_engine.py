class EngineService:
    def process_payload(self, text: str) -> dict:
        import re
        try:
            re.compile(text)
            return {'status': 'VALID', 'data': 'Pattern compiled successfully.'}
        except re.error as e:
            return {'status': 'ERROR', 'data': str(e)}

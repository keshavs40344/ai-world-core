class EngineService:
    def process_payload(self, text: str) -> dict:
        import re
        try:
            pattern = text.strip()
            test_string = "Sample input for validation"
            match = re.search(pattern, test_string)
            return {'status': 'VALID', 'data': 'Match found' if match else 'No match'}
        except re.error as e:
            return {'status': 'ERROR', 'data': str(e)}

import re

class EngineService:
    def process_payload(self, text: str) -> dict:
        try:
            pattern, test_string = text.split('|', 1)
            match = re.search(pattern, test_string)
            return {'status': 'MATCHED' if match else 'NO_MATCH', 'data': match.group(0) if match else ''}
        except Exception:
            return {'status': 'ERROR', 'data': 'Invalid input format or regex error'}

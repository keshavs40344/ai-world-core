import re

class EngineService:
    def process_payload(self, text: str) -> dict:
        try:
            pattern, test_string = text.split('|', 1)
            matches = re.findall(pattern, test_string)
            return {'status': 'PASSED', 'data': matches}
        except Exception as e:
            return {'status': 'FAILED', 'data': str(e)}

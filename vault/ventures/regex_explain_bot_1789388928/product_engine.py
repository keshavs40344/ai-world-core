import re
class EngineService:
    def process_payload(self, text: str) -> dict:
        try:
            pattern, test_string = text.split('|', 1)
            match = re.search(pattern, test_string)
            return {'status': 'PASSED', 'data': {'matched': bool(match), 'pattern': pattern, 'test_input': test_string}}
        except Exception as e:
            return {'status': 'FAILED', 'data': {'error': str(e)}}

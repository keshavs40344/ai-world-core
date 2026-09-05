import re

class EngineService:
    def process_payload(self, text: str) -> dict:
        try:
            pattern = text.strip()
            compiled = re.compile(pattern)
            test_string = "Sample Test String 123"
            match = compiled.search(test_string)
            return {
                'status': 'VALID',
                'data': {
                    'pattern': pattern,
                    'match_found': bool(match),
                    'groups': match.groupdict() if match else {}
                }
            }
        except re.error as e:
            return {'status': 'INVALID', 'data': {'error': str(e)}}

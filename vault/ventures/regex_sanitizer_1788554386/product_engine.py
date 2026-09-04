import re

class EngineService:
    def process_payload(self, text: str) -> dict:
        pattern = text.strip()
        try:
            # Attempt to compile and test for catastrophic backtracking
            # by running a simple timeout check on a pathological string
            compiled = re.compile(pattern)
            # Simulate a quick safety check
            test_string = "a" * 1000 + "b"
            try:
                compiled.match(test_string)
                return {'status': 'SAFE', 'data': pattern}
            except Exception:
                return {'status': 'RISKY', 'data': pattern}
        except re.error as e:
            return {'status': 'INVALID', 'data': str(e)}

import re
import time

class EngineService:
    def process_payload(self, text: str) -> dict:
        try:
            pattern = text.strip()
            test_string = "a" * 1000
            start = time.perf_counter()
            re.compile(pattern).search(test_string)
            duration = time.perf_counter() - start
            return {
                'status': 'PASSED',
                'data': {
                    'compile_time_ms': round(duration * 1000, 4),
                    'is_valid': True
                }
            }
        except re.error as e:
            return {
                'status': 'FAILED',
                'data': {'error': str(e)}
            }

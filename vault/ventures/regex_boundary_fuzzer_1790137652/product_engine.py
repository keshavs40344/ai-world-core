import re
import time

class EngineService:
    def process_payload(self, text: str) -> dict:
        try:
            pattern = text.strip()
            test_string = "a" * 10000
            start = time.time()
            re.search(pattern, test_string)
            duration = time.time() - start
            status = 'PASSED' if duration < 1.0 else 'TIMEOUT_RISK'
            return {'status': status, 'data': f'Execution time: {duration:.4f}s'}
        except Exception as e:
            return {'status': 'FAILED', 'data': str(e)}

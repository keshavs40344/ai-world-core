class EngineService:
    def process_payload(self, text: str) -> dict:
        import re
        import time
        try:
            pattern = text.strip()
            test_string = 'a' * 1000
            start = time.perf_counter()
            re.search(pattern, test_string)
            end = time.perf_counter()
            duration = end - start
            status = 'PASSED' if duration < 0.1 else 'SLOW'
            return {'status': status, 'data': f'Execution time: {duration:.4f}s'}
        except re.error as e:
            return {'status': 'ERROR', 'data': str(e)}

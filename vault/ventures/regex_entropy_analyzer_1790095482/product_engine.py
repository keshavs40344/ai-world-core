import re
import time

class EngineService:
    def process_payload(self, text: str) -> dict:
        try:
            start_time = time.perf_counter()
            # Attempt to compile and test against a benign string to measure overhead
            pattern = re.compile(text)
            pattern.match('test_string_for_benchmarking')
            compile_time = time.perf_counter() - start_time
            
            # Simple heuristic: count quantifiers and nested groups as complexity indicators
            complexity_score = text.count('*') + text.count('+') + text.count('{') + text.count('(')
            
            return {
                'status': 'PASSED',
                'data': {
                    'compile_time_ms': round(compile_time * 1000, 4),
                    'complexity_heuristic': complexity_score,
                    'is_valid': True
                }
            }
        except re.error:
            return {
                'status': 'FAILED',
                'data': {
                    'is_valid': False,
                    'error': 'Invalid regex syntax'
                }
            }

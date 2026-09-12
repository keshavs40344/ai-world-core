import re
import time

class EngineService:
    def process_payload(self, text: str) -> dict:
        try:
            pattern = text.strip()
            # Simulate a basic complexity check by compiling and timing a dummy match
            start_time = time.time()
            re.compile(pattern)
            end_time = time.time()
            compile_time = end_time - start_time
            
            # Heuristic: If compile time is high or pattern is very long, flag as potentially slow
            is_potentially_slow = compile_time > 0.001 or len(pattern) > 100
            
            return {
                'status': 'PASSED',
                'data': {
                    'is_valid': True,
                    'compile_time_ms': round(compile_time * 1000, 4),
                    'warning': 'High complexity detected' if is_potentially_slow else None
                }
            }
        except re.error as e:
            return {
                'status': 'FAILED',
                'data': {
                    'is_valid': False,
                    'error': str(e)
                }
            }

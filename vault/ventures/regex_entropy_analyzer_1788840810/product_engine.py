import re
import time

class EngineService:
    def process_payload(self, text: str) -> dict:
        try:
            pattern = text.strip()
            compiled = re.compile(pattern)
            
            # Simple heuristic: count quantifiers and alternations as complexity indicators
            complexity_score = 0
            for char in pattern:
                if char in '*+?{}|':
                    complexity_score += 1
            
            # Basic performance test with a benign string
            start_time = time.perf_counter()
            for _ in range(1000):
                compiled.search('test string for benchmarking')
            end_time = time.perf_counter()
            
            avg_time = (end_time - start_time) / 1000
            
            return {
                'status': 'PASSED',
                'data': {
                    'valid_regex': True,
                    'complexity_score': complexity_score,
                    'avg_match_time_ns': int(avg_time * 1e9),
                    'risk_level': 'HIGH' if avg_time > 0.001 else 'LOW'
                }
            }
        except re.error:
            return {
                'status': 'FAILED',
                'data': {'valid_regex': False, 'error': 'Invalid regex syntax'}
            }
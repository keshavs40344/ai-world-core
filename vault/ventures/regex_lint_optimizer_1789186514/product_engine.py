import re
import time

class EngineService:
    def process_payload(self, text: str) -> dict:
        try:
            start_time = time.time()
            # Attempt to compile to check syntax
            pattern = re.compile(text)
            compile_time = time.time() - start_time
            
            # Basic heuristic check for potential backtracking risks (nested quantifiers)
            risk_score = 0
            if '.*' in text or '+*' in text or '++' in text:
                risk_score = 10
            
            return {
                'status': 'PASSED',
                'data': {
                    'valid_syntax': True,
                    'compile_time_ms': round(compile_time * 1000, 4),
                    'risk_score': risk_score,
                    'pattern_length': len(text)
                }
            }
        except re.error as e:
            return {
                'status': 'FAILED',
                'data': {
                    'valid_syntax': False,
                    'error_message': str(e)
                }
            }

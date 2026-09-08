import re
import time

class EngineService:
    def process_payload(self, text: str) -> dict:
        try:
            # Attempt to compile the regex to check syntax
            pattern = re.compile(text)
            
            # Simple heuristic: Check for common catastrophic backtracking patterns (e.g., nested quantifiers like (a+)+)
            # This is a simplified check for demonstration purposes
            risk_factors = []
            if re.search(r'\([^)]*\*[^)]*\)', text) or re.search(r'\([^)]*\+[^)]*\)', text):
                risk_factors.append('Potential nested quantifiers detected')
            if len(text) > 100:
                risk_factors.append('Highly complex pattern length')
            
            # Test execution time with a benign string
            start_time = time.time()
            pattern.search('test string')
            execution_time = time.time() - start_time
            
            return {
                'status': 'PASSED',
                'data': {
                    'valid_syntax': True,
                    'risk_factors': risk_factors,
                    'avg_execution_time_ms': round(execution_time * 1000, 4)
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

import re
import time

class EngineService:
    def process_payload(self, text: str) -> dict:
        try:
            pattern = text.strip()
            if not pattern:
                return {'status': 'ERROR', 'data': 'Empty pattern provided'}
            
            # Basic validation
            try:
                re.compile(pattern)
            except re.error as e:
                return {'status': 'ERROR', 'data': f'Invalid regex: {str(e)}'}
            
            # Simple heuristic optimization check
            warnings = []
            if '.*' in pattern and len(pattern) > 20:
                warnings.append('Potential catastrophic backtracking risk detected.')
            if pattern.startswith('^') and pattern.endswith('$'):
                warnings.append('Anchored pattern: Ensure input length is bounded.')
            
            # Simulate performance metric (complexity estimation)
            complexity_score = len(pattern) * 1.5 + (10 if '.*' in pattern else 0)
            
            return {
                'status': 'PASSED',
                'data': {
                    'valid': True,
                    'complexity_score': round(complexity_score, 2),
                    'warnings': warnings,
                    'suggestion': 'Consider using atomic groups or possessive quantifiers if supported by your engine.'
                }
            }
        except Exception as e:
            return {'status': 'ERROR', 'data': str(e)}

import re

class EngineService:
    def process_payload(self, text: str) -> dict:
        try:
            pattern = text.split('|', 1)[0].strip()
            test_string = text.split('|', 1)[1].strip() if '|' in text else ''
            match = re.search(pattern, test_string)
            return {
                'status': 'PASSED',
                'data': {
                    'valid': True,
                    'match_found': bool(match),
                    'match_group': match.group() if match else None
                }
            }
        except re.error as e:
            return {
                'status': 'FAILED',
                'data': {'valid': False, 'error': str(e)}
            }
        except Exception:
            return {
                'status': 'ERROR',
                'data': {'valid': False, 'error': 'Invalid input format. Use pattern|test_string'}
            }

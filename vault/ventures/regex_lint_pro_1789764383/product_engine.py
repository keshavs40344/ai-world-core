import re

class EngineService:
    def process_payload(self, text: str) -> dict:
        try:
            pattern, sample = text.split('|', 1)
            regex = re.compile(pattern)
            matches = regex.findall(sample)
            return {'status': 'VALID', 'matches': matches}
        except ValueError:
            return {'status': 'ERROR', 'message': 'Invalid input format. Use: regex|sample_text'}
        except re.error as e:
            return {'status': 'INVALID_REGEX', 'message': str(e)}

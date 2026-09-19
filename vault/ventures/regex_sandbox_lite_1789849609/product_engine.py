import re
class EngineService:
    def process_payload(self, text: str) -> dict:
        try:
            pattern = text.split('|', 1)[0]
            sample = text.split('|', 1)[1] if '|' in text else ''
            matches = re.findall(pattern, sample)
            return {'status': 'PASSED', 'data': {'matches': matches, 'count': len(matches)}}
        except re.error as e:
            return {'status': 'ERROR', 'data': {'message': str(e)}}

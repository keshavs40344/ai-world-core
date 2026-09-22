class EngineService:
    def process_payload(self, text: str) -> dict:
        import re
        try:
            pattern = text.split('|', 1)[0] if '|' in text else text
            sample = text.split('|', 1)[1] if '|' in text else ''
            match = re.search(pattern, sample)
            return {'status': 'PASSED', 'data': {'match': bool(match), 'span': match.span() if match else None}}
        except re.error as e:
            return {'status': 'FAILED', 'data': {'error': str(e)}}

import re

class EngineService:
    def process_payload(self, text: str) -> dict:
        try:
            pattern = text.split('|')[-1]
            sample = text.split('|')[0]
            match = re.search(pattern, sample)
            return {'status': 'MATCHED' if match else 'NO_MATCH', 'data': match.group(0) if match else None}
        except Exception as e:
            return {'status': 'ERROR', 'data': str(e)}

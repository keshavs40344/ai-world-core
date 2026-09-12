import re

class EngineService:
    def process_payload(self, text: str) -> dict:
        # Sanitize by removing potential injection characters and normalizing whitespace
        sanitized = re.sub(r'[^\w\s-]', '', text).strip()
        return {'status': 'SANITIZED', 'data': sanitized}
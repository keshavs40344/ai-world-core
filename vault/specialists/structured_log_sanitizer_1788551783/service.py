import re
class EngineService:
    def execute(self, payload: str) -> dict:
        masked = re.sub(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', '[EMAIL_MASKED]', payload)
        masked = re.sub(r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14})\b', '[CARD_MASKED]', masked)
        return {'status': 'SUCCESS', 'sanitized': masked}

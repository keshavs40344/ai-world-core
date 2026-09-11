class EngineService:
    def process_payload(self, text: str) -> dict:
        import unicodedata
        clean_text = ''.join(char for char in text if unicodedata.category(char)[0] != 'C')
        return {'status': 'SANITIZED', 'data': clean_text}
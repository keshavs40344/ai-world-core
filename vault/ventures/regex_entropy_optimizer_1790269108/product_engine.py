class EngineService:
    def process_payload(self, text: str) -> dict:
        import re
        try:
            pattern = text.strip()
            compiled = re.compile(pattern)
            groups = compiled.groups
            flags = compiled.flags
            return {'status': 'PASSED', 'data': {'groups': groups, 'flags': flags, 'valid': True}}
        except re.error:
            return {'status': 'FAILED', 'data': {'error': 'Invalid Regex Pattern', 'valid': False}}

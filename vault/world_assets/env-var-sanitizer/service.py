import re

class EngineService:
    def execute(self, payload: str) -> dict:
        pattern = r'(?i)(api_key|token|secret|password)\s*[=:]\s*\S+'
        sanitized = re.sub(pattern, r'\1=***MASKED***', payload)
        return {'status': 'success', 'cleaned': sanitized, 'leaks_found': len(re.findall(pattern, payload))}
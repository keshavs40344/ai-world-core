import re

class EngineService:
    def process_payload(self, text: str) -> dict:
        pattern = r'^(feat|fix|docs|style|refactor|perf|test|build|ci|chore)(\(.+\))?: .{3,}'
        match = re.match(pattern, text.strip())
        if match:
            return {'status': 'VALID', 'type': match.group(1), 'scope': match.group(2) if match.group(2) else None}
        else:
            return {'status': 'INVALID', 'error': 'Commit message does not follow Conventional Commits spec.'}

class EngineService:
    def process_payload(self, text: str) -> dict:
        import re
        pattern = r'^(feat|fix|docs|style|refactor|perf|test|build|ci|chore)(\(.+\))?!?: .{5,}'
        match = re.match(pattern, text.strip())
        return {'status': 'PASSED' if match else 'FAILED', 'data': text.strip()}

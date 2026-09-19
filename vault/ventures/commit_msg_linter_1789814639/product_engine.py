class EngineService:
    def process_payload(self, text: str) -> dict:
        import re
        pattern = r'^(feat|fix|docs|style|refactor|perf|test|build|ci|chore)(\(.+\))?: .{5,}'
        is_valid = bool(re.match(pattern, text.strip()))
        return {
            'status': 'PASSED' if is_valid else 'FAILED',
            'data': {
                'valid': is_valid,
                'message': text.strip()
            }
        }
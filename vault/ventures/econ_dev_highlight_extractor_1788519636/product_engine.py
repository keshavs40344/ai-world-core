class EngineService:
    def process_payload(self, text: str) -> dict:
        import re
        # Simple heuristic to find lines following 'Highlights:'
        lines = text.split('\n')
        highlights = []
        in_highlights = False
        for line in lines:
            if 'Highlights:' in line:
                in_highlights = True
                continue
            if in_highlights:
                if line.strip() and not line.startswith('www.') and not line.startswith('['):
                    highlights.append(line.strip())
                else:
                    break
        return {'status': 'PASSED', 'data': highlights}
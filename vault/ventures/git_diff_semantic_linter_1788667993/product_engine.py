class EngineService:
    def process_payload(self, text: str) -> dict:
        lines = text.strip().split('\n')
        semantic_changes = []
        for line in lines:
            if line.startswith('+') and not line.startswith('+++'):
                content = line[1:].strip()
                if content and not content.startswith('#'):
                    semantic_changes.append(content)
        return {'status': 'PASSED', 'data': {'semantic_lines': semantic_changes, 'count': len(semantic_changes)}}
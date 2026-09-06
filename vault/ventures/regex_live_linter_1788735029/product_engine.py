import re

class EngineService:
    def process_payload(self, text: str) -> dict:
        # Expecting text format: "pattern|test_string"
        try:
            parts = text.split('|', 1)
            if len(parts) != 2:
                return {'status': 'ERROR', 'data': 'Invalid input format. Use pattern|test_string'}
            
            pattern, test_string = parts
            match = re.search(pattern, test_string)
            
            if match:
                return {
                    'status': 'MATCH',
                    'data': {
                        'matched_text': match.group(),
                        'start': match.start(),
                        'end': match.end(),
                        'groups': match.groups()
                    }
                }
            else:
                return {'status': 'NO_MATCH', 'data': None}
        except re.error as e:
            return {'status': 'SYNTAX_ERROR', 'data': str(e)}

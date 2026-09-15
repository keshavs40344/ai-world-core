import re

class EngineService:
    def process_payload(self, text: str) -> dict:
        try:
            # Simple heuristic extraction for demonstration
            match = re.search(r'(GET|POST|PUT|DELETE|PATCH)\s+(\S+)', text)
            if not match:
                return {'status': 'FAILED', 'data': 'No valid HTTP request found in input.'}
            
            method = match.group(1)
            url = match.group(2)
            
            # Constructing a basic curl command
            curl_cmd = f"curl -X {method} '{url}'"
            
            return {'status': 'PASSED', 'data': curl_cmd}
        except Exception as e:
            return {'status': 'ERROR', 'data': str(e)}

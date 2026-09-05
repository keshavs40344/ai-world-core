class EngineService:
    def process_payload(self, text: str) -> dict:
        import json
        try:
            spec = json.loads(text)
            endpoints = []
            if 'paths' in spec:
                for path, methods in spec['paths'].items():
                    for method in methods:
                        if method in ['get', 'post', 'put', 'delete', 'patch']:
                            endpoints.append(f"{method.upper()} {path}")
            return {'status': 'PASSED', 'data': {'endpoints': endpoints, 'count': len(endpoints)}}
        except json.JSONDecodeError:
            return {'status': 'ERROR', 'data': 'Invalid JSON'}
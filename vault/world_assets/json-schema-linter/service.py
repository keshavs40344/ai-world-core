class EngineService:
    def execute(self, payload: str) -> dict:
        import json
        try:
            data = json.loads(payload)
            schema = json.loads(data.get('schema', '{}'))
            obj = data.get('object', {})
            errors = []
            for key, rule in schema.items():
                if key not in obj: errors.append(f'Missing: {key}')
                elif not isinstance(obj[key], rule.get('type', type(None))): errors.append(f'Type mismatch: {key}')
            return {'valid': len(errors) == 0, 'errors': errors}
        except Exception as e:
            return {'valid': False, 'errors': [str(e)]}
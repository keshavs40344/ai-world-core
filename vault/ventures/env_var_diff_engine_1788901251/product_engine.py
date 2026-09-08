class EngineService:
    def process_payload(self, text: str) -> dict:
        import json
        try:
            data = json.loads(text)
            if not isinstance(data, dict) or 'local' not in data or 'prod' not in data:
                return {'status': 'ERROR', 'message': 'Invalid JSON structure. Expected keys: local, prod'}
            local_vars = data['local']
            prod_vars = data['prod']
            
            added_in_prod = set(prod_vars.keys()) - set(local_vars.keys())
            missing_in_prod = set(local_vars.keys()) - set(prod_vars.keys())
            value_mismatches = {k: {'local': local_vars[k], 'prod': prod_vars[k]} for k in local_vars if k in prod_vars and local_vars[k] != prod_vars[k]}
            
            return {
                'status': 'SUCCESS',
                'data': {
                    'added_in_prod': list(added_in_prod),
                    'missing_in_prod': list(missing_in_prod),
                    'value_mismatches': value_mismatches
                }
            }
        except json.JSONDecodeError:
            return {'status': 'ERROR', 'message': 'Invalid JSON input'}
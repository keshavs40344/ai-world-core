class EngineService:
    def execute(self, payload: str) -> dict:
        import json
        try:
            data = json.loads(payload)
            def flatten(d, prefix=''):
                items = []
                for k, v in d.items():
                    key = f"{prefix}_{k}".upper().replace('-', '_')
                    if isinstance(v, dict): items.extend(flatten(v, key))
                    else: items.append(f"{key}={v}")
                return items
            return {'status': 'success', 'env_vars': flatten(data)}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
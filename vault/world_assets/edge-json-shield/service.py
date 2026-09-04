import json
import re

class EngineService:
    def execute(self, payload: str) -> dict:
        try:
            data = json.loads(payload)
            if not isinstance(data, (dict, list)):
                return {'status': 'ERROR', 'code': 'INVALID_ROOT', 'message': 'Root must be object or array'}
            
            # Lightweight sanitization: Remove keys with null values to reduce payload size
            def sanitize(obj):
                if isinstance(obj, dict):
                    return {k: sanitize(v) for k, v in obj.items() if v is not None}
                elif isinstance(obj, list):
                    return [sanitize(i) for i in obj if i is not None]
                return obj

            cleaned = sanitize(data)
            return {
                'status': 'SUCCESS',
                'result': cleaned,
                'metrics': {
                    'original_size': len(payload),
                    'cleaned_size': len(json.dumps(cleaned)),
                    'keys_count': len(cleaned) if isinstance(cleaned, dict) else len(cleaned)
                }
            }
        except json.JSONDecodeError as e:
            return {'status': 'ERROR', 'code': 'PARSE_FAIL', 'message': str(e)}
        except Exception as e:
            return {'status': 'ERROR', 'code': 'INTERNAL', 'message': str(e)}
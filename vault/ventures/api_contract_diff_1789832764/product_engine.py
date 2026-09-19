import json
import difflib

class EngineService:
    def process_payload(self, text: str) -> dict:
        try:
            payload = json.loads(text)
            old_spec = payload.get('old', {})
            new_spec = payload.get('new', {})
            
            # Simplified logic: Compare paths and operations
            old_paths = set(old_spec.get('paths', {}).keys())
            new_paths = set(new_spec.get('paths', {}).keys())
            
            added_paths = list(new_paths - old_paths)
            removed_paths = list(old_paths - new_paths)
            
            # Check for operation changes in common paths
            changed_operations = []
            for path in old_paths.intersection(new_paths):
                old_ops = old_spec['paths'].get(path, {})
                new_ops = new_spec['paths'].get(path, {})
                for method in ['get', 'post', 'put', 'delete', 'patch']:
                    if method in old_ops or method in new_ops:
                        if old_ops.get(method) != new_ops.get(method):
                            changed_operations.append(f"{method.upper()} {path}")

            return {
                'status': 'PASSED',
                'data': {
                    'added_paths': added_paths,
                    'removed_paths': removed_paths,
                    'changed_operations': changed_operations,
                    'is_breaking': bool(removed_paths or changed_operations)
                }
            }
        except json.JSONDecodeError:
            return {'status': 'FAILED', 'data': 'Invalid JSON format'}

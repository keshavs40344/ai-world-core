import json
import zlib

class EngineService:
    def execute(self, payload: str) -> dict:
        try:
            data = json.loads(payload)
            compressed = zlib.compress(json.dumps(data).encode('utf-8'))
            return {
                'status': 'success',
                'compressed_size': len(compressed),
                'original_size': len(payload),
                'data_hash': hash(compressed)
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
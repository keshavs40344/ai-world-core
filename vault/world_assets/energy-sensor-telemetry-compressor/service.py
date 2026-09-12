import zlib, json

class EngineService:
    def execute(self, payload: str) -> dict:
        try:
            data = json.loads(payload)
            compressed = zlib.compress(json.dumps(data).encode(), 9)
            return {
                'status': 'success',
                'original_size': len(payload),
                'compressed_size': len(compressed),
                'ratio': round(len(compressed)/len(payload), 4),
                'data': compressed.hex()
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
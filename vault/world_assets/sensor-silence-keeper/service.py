import zlib, json
class EngineService:
    def execute(self, payload: str) -> dict:
        try:
            data = json.loads(payload)
            compressed = zlib.compress(json.dumps(data).encode('utf-8'))
            return {'status': 'ok', 'compressed_size': len(compressed), 'data': compressed.hex()}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
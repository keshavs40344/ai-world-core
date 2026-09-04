class EngineService:
    import json
    import base64
    import zlib

    def execute(self, payload: str) -> dict:
        try:
            data = json.loads(payload)
            compressed = zlib.compress(json.dumps(data, separators=(',', ':')).encode('utf-8'))
            b64 = base64.b64encode(compressed).decode('utf-8')
            return {
                'status': 'SUCCESS',
                'compressed_payload': b64,
                'original_size': len(payload),
                'compressed_size': len(b64),
                'compression_ratio': round(len(b64) / len(payload), 2)
            }
        except Exception as e:
            return {'status': 'ERROR', 'message': str(e)}
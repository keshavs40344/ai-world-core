class EngineService:
    def execute(self, payload: str) -> dict:
        import json, zlib
        try:
            data = json.loads(payload)
            compressed = zlib.compress(json.dumps(data).encode('utf-8'), 9)
            return {"status": "success", "size_original": len(payload), "size_compressed": len(compressed), "data": compressed.hex()}
        except Exception as e:
            return {"status": "error", "message": str(e)}
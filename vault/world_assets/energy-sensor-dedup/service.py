import json, zlib

class EngineService:
    def execute(self, payload: str) -> dict:
        try:
            data = json.loads(payload)
            unique = list(dict.fromkeys(data))
            compressed = zlib.compress(json.dumps(unique).encode())
            return {"status": "ok", "original": len(data), "deduped": len(unique), "compressed_size": len(compressed)}
        except Exception as e:
            return {"status": "error", "message": str(e)}
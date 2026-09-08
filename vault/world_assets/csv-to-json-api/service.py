import csv, io, json

class EngineService:
    def execute(self, payload: str) -> dict:
        try:
            reader = csv.DictReader(io.StringIO(payload))
            data = [dict(row) for row in reader]
            return {"status": "success", "data": data}
        except Exception as e:
            return {"status": "error", "message": str(e)}
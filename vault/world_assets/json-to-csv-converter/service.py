import json, csv, io

class EngineService:
    def execute(self, payload: str) -> dict:
        try:
            data = json.loads(payload)
            if not isinstance(data, list) or not data:
                return {"error": "Invalid JSON array"}
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
            return {"csv": output.getvalue()}
        except Exception as e:
            return {"error": str(e)}
class EngineService:
    def execute(self, payload: str) -> dict:
        import csv, io, json
        lines = payload.strip().split('\n')
        if not lines: return {'status': 'ERROR', 'message': 'Empty input'}
        reader = csv.DictReader(io.StringIO(payload))
        data = [dict(row) for row in reader]
        return {'status': 'SUCCESS', 'result': json.dumps(data, indent=2)}

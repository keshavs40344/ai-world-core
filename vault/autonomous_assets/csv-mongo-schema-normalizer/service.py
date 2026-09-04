import json, csv, io

class EngineService:
    def execute(self, payload: str) -> dict:
        try:
            reader = csv.DictReader(io.StringIO(payload))
            schema = {}
            docs = []
            for row in reader:
                doc = {}
                for k, v in row.items():
                    if v == '': continue
                    if v.lower() in ['true', 'false']: t = 'bool'
                    elif v.replace('.', '', 1).isdigit(): t = 'int' if '.' not in v else 'float'
                    else: t = 'str'
                    schema.setdefault(k, set()).add(t)
                    doc[k] = json.loads(v) if t in ['bool', 'int', 'float'] else v
                docs.append(doc)
            final_schema = {k: list(v)[0] if len(v) == 1 else 'mixed' for k, v in schema.items()}
            return {'status': 'success', 'schema': final_schema, 'documents': docs, 'count': len(docs)}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
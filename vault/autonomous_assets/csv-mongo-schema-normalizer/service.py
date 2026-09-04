import json, csv, io

class EngineService:
    def execute(self, payload: str) -> dict:
        try:
            data = json.loads(payload)
            csv_text = data.get('csv_data', '')
            reader = csv.DictReader(io.StringIO(csv_text))
            type_map = {}
            normalized = []
            for row in reader:
                norm_row = {}
                for k, v in row.items():
                    if v == '': v = None
                    elif v.lower() in ['true', 'false']: v = v.lower() == 'true'
                    else:
                        try: v = int(v)
                        except: 
                            try: v = float(v)
                            except: pass
                    norm_row[k] = v
                    if k not in type_map: type_map[k] = type(v).__name__
                    elif type_map[k] != type(v).__name__: type_map[k] = 'mixed'
                normalized.append(norm_row)
            return {'status': 'success', 'documents': normalized, 'schema': type_map}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
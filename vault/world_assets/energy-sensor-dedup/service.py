import json

class EngineService:
    def execute(self, payload: str) -> dict:
        try:
            data = json.loads(payload)
            points = data.get('points', [])
            unique = []
            last_val = None
            for p in points:
                if p['val'] != last_val:
                    unique.append(p)
                    last_val = p['val']
            return {'status': 'ok', 'original': len(points), 'compressed': len(unique), 'data': unique}
        except Exception as e:
            return {'status': 'error', 'msg': str(e)}
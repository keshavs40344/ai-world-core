class EngineService:
    def execute(self, payload: str) -> dict:
        import json
        try:
            data = json.loads(payload)
            temp = data.get('temp', 0)
            pressure = data.get('pressure', 0)
            compliant = temp < 85 and pressure < 100
            risk = 'HIGH' if not compliant else 'LOW'
            return {'status': 'ok', 'compliant': compliant, 'risk': risk, 'metrics': {'temp': temp, 'pressure': pressure}}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
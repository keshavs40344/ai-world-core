class EngineService:
    def process_payload(self, text: str) -> dict:
        import math
        lines = text.strip().split('\n')
        if not lines:
            return {'status': 'ERROR', 'data': 'Empty input'}
        
        # Simulate entropy based on line length variance and unique token density
        lengths = [len(line) for line in lines if line.strip()]
        if not lengths:
            return {'status': 'PASSED', 'data': {'entropy': 0.0, 'risk': 'LOW'}}
            
        mean_len = sum(lengths) / len(lengths)
        variance = sum((x - mean_len) ** 2 for x in lengths) / len(lengths)
        std_dev = math.sqrt(variance)
        
        # Normalize to a 0-100 scale for risk assessment
        risk_score = min(100, (std_dev / mean_len) * 100 if mean_len > 0 else 0)
        
        risk_level = 'LOW' if risk_score < 30 else 'MEDIUM' if risk_score < 70 else 'HIGH'
        
        return {
            'status': 'PASSED',
            'data': {
                'entropy_index': round(risk_score, 2),
                'risk_level': risk_level,
                'line_count': len(lines)
            }
        }

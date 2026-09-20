class EngineService:
    def process_payload(self, text: str) -> dict:
        import time
        import json
        
        # Parse input as JSON if possible, otherwise treat as raw string
        try:
            config = json.loads(text)
            threshold_ms = config.get('threshold_ms', 200)
            endpoint_name = config.get('endpoint', 'unknown')
        except json.JSONDecodeError:
            threshold_ms = 200
            endpoint_name = text.strip()

        # Simulate a latency check (in a real scenario, this would ping the endpoint)
        # Here we simulate a random latency for demonstration
        import random
        simulated_latency = random.randint(50, 500)
        
        status = 'PASS' if simulated_latency <= threshold_ms else 'FAIL'
        
        return {
            'status': status,
            'data': {
                'endpoint': endpoint_name,
                'simulated_latency_ms': simulated_latency,
                'threshold_ms': threshold_ms,
                'within_budget': simulated_latency <= threshold_ms
            }
        }

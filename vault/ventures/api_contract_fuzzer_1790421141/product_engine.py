import json
import random
import string

class EngineService:
    def process_payload(self, text: str) -> dict:
        try:
            schema = json.loads(text)
            if not isinstance(schema, dict):
                raise ValueError("Root must be an object")
            
            def generate_value(key, value):
                if isinstance(value, dict):
                    return {k: generate_value(k, v) for k, v in value.items()}
                elif isinstance(value, list):
                    return [generate_value(f"{key}_{i}", v) for i, v in enumerate(value[:3])]
                elif value == "string":
                    return ''.join(random.choices(string.ascii_lowercase, k=8))
                elif value == "integer":
                    return random.randint(1, 1000)
                elif value == "boolean":
                    return random.choice([True, False])
                else:
                    return value

            generated = {k: generate_value(k, v) for k, v in schema.items()}
            return {
                'status': 'PASSED',
                'data': json.dumps(generated, indent=2)
            }
        except Exception as e:
            return {
                'status': 'FAILED',
                'data': f"Invalid schema: {str(e)}"
            }

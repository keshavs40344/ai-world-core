import re

class EngineService:
    def process_payload(self, text: str) -> dict:
        """
        Expects JSON string: {"pattern": "...", "test_cases": ["...", "..."]}
        Returns validation status and match results.
        """
        try:
            import json
            payload = json.loads(text)
            pattern = payload.get('pattern', '')
            test_cases = payload.get('test_cases', [])
            
            # Compile to check for syntax errors
            compiled = re.compile(pattern)
            
            results = []
            for case in test_cases:
                match = compiled.search(case)
                results.append({
                    "input": case,
                    "matched": bool(match),
                    "group": match.group() if match else None
                })
                
            return {
                "status": "PASSED",
                "data": {
                    "valid_syntax": True,
                    "results": results
                }
            }
        except re.error as e:
            return {
                "status": "FAILED",
                "data": {
                    "valid_syntax": False,
                    "error": str(e)
                }
            }
        except Exception as e:
            return {
                "status": "ERROR",
                "data": {
                    "error": "Invalid payload format"
                }
            }

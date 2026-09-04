import re
import json

class EngineService:
    def execute(self, payload: str) -> dict:
        """
        Analyzes raw GitHub issue text to identify friction points.
        """
        if not payload:
            return {'status': 'ERROR', 'message': 'Empty payload'}

        # Simple heuristic keyword mapping for friction categories
        friction_map = {
            'documentation': ['docs', 'documentation', 'readme', 'guide', 'unclear', 'missing info'],
            'environment': ['env', 'environment', 'setup', 'install', 'docker', 'k8s', 'config', 'missing dependency'],
            'bug': ['bug', 'error', 'crash', 'fail', 'exception', 'traceback', '500', '404'],
            'performance': ['slow', 'latency', 'timeout', 'memory leak', 'cpu', 'performance']
        }

        text_lower = payload.lower()
        findings = []
        
        for category, keywords in friction_map.items():
            # Check if any keyword is present
            if any(kw in text_lower for kw in keywords):
                # Extract a snippet around the first occurrence for context
                first_kw = next(kw for kw in keywords if kw in text_lower)
                idx = text_lower.find(first_kw)
                start = max(0, idx - 50)
                end = min(len(payload), idx + len(first_kw) + 50)
                snippet = payload[start:end].strip()
                findings.append({
                    'category': category,
                    'confidence': 'high' if len([kw for kw in keywords if kw in text_lower]) > 1 else 'medium',
                    'context_snippet': snippet
                })

        # Deduplicate findings by category, keeping the one with higher confidence or longer snippet
        unique_findings = {}
        for f in findings:
            cat = f['category']
            if cat not in unique_findings:
                unique_findings[cat] = f
            else:
                # Keep the one with more context or higher confidence
                if len(f['context_snippet']) > len(unique_findings[cat]['context_snippet']):
                    unique_findings[cat] = f

        return {
            'status': 'SUCCESS',
            'friction_points': list(unique_findings.values()),
            'total_categories_detected': len(unique_findings)
        }

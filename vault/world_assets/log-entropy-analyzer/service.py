import math
from collections import Counter

class EngineService:
    def execute(self, payload: str) -> dict:
        logs = payload.split('\n')
        counts = Counter(logs)
        total = len(logs)
        entropy = -sum((c/total) * math.log2(c/total) for c in counts.values() if c > 0)
        return {'entropy': round(entropy, 4), 'unique_logs': len(counts), 'total_logs': total, 'noise_ratio': round(1 - (max(counts.values())/total), 4)}
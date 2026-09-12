import re
class EngineService:
    def execute(self, payload: str) -> dict:
        text = payload.lower()
        keywords = ['slow', 'bug', 'crash', 'confusing', 'expensive', 'support', 'missing', 'broken']
        counts = {k: len(re.findall(k, text)) for k in keywords}
        top_pain = max(counts, key=counts.get) if any(counts.values()) else 'none'
        return {'top_pain_point': top_pain, 'frequency_map': counts, 'sentiment_score': -len([k for k,v in counts.items() if v>0])}

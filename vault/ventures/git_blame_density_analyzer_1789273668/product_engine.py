class EngineService:
    def process_payload(self, text: str) -> dict:
        lines = text.strip().split('\n')
        if not lines:
            return {'status': 'EMPTY', 'data': {}}
        
        # Simulate parsing git log --numstat or similar density data
        # Format expected: <commit_hash> <author> <lines_changed>
        density_map = {}
        for line in lines:
            parts = line.split()
            if len(parts) >= 3:
                author = parts[1]
                try:
                    changes = int(parts[2])
                except ValueError:
                    continue
                density_map[author] = density_map.get(author, 0) + changes
        
        # Calculate top contributors by churn
        sorted_authors = sorted(density_map.items(), key=lambda x: x[1], reverse=True)
        top_risk = sorted_authors[:5]
        
        return {
            'status': 'ANALYZED',
            'data': {
                'total_authors': len(density_map),
                'top_risk_contributors': top_risk,
                'total_churn': sum(density_map.values())
            }
        }

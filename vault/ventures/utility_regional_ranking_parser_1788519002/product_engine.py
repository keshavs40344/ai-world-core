import re

class EngineService:
    def process_payload(self, text: str) -> dict:
        # Define regions to look for (based on context)
        regions = ['SOUTH CENTRAL', 'NORTHEAST', 'MIDWEST', 'SOUTHWEST', 'WEST']
        
        # Regex to capture Region, Company, City, State, Person, Title, URL
        # This is a simplified heuristic parser for the specific format provided
        pattern = r"""
        (?P<region>""" + '|'.join(regions) + r"""
        )\s*
        (?P<company>[\w\s&-]+?)\s*
        (?P<city>[\w\s-]+),\s*(?P<state>[A-Z]{2})\s*
        (?P<person>[\w\s-]+),\s*(?P<title>[\w\s&-]+?)\s*
        (?P<url>https?://[\w\.-]+[\w\./-]*)
        """
        
        matches = re.findall(pattern, text, re.VERBOSE | re.IGNORECASE)
        
        results = []
        for match in matches:
            results.append({
                'region': match[0].strip(),
                'company': match[1].strip(),
                'location': f"{match[2].strip()}, {match[3].strip()}",
                'contact': match[4].strip(),
                'title': match[5].strip(),
                'url': match[6].strip()
            })

        return {
            'status': 'SUCCESS' if results else 'NO_DATA_FOUND',
            'count': len(results),
            'data': results
        }

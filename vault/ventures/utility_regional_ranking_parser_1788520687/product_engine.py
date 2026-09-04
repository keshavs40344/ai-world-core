import re

class EngineService:
    def process_payload(self, text: str) -> dict:
        # Simple heuristic parser for the specific format described
        # Format: Region, Company, City, State, Person, Title, URL
        entries = []
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        i = 0
        while i < len(lines):
            line = lines[i]
            # Check if line looks like a region header (all caps, short)
            if line.isupper() and len(line) < 30 and not line.startswith('HTTP') and not line.startswith('WWW'):
                region = line
                # Look ahead for company name (next non-empty line that isn't a URL or person)
                if i + 1 < len(lines):
                    company = lines[i+1]
                    # Look ahead for city/state
                    if i + 2 < len(lines):
                        location = lines[i+2]
                        # Look ahead for person
                        if i + 3 < len(lines):
                            person_line = lines[i+3]
                            # Parse person and title if possible (simplified)
                            person = person_line.split(',')[0] if ',' in person_line else person_line
                            title = person_line.split(',', 1)[1].strip() if ',' in person_line else ''
                            # Look ahead for URL
                            url = ''
                            if i + 4 < len(lines) and lines[i+4].startswith('www'):
                                url = lines[i+4]
                                i += 1
                            
                            entries.append({
                                'region': region,
                                'company': company,
                                'location': location,
                                'contact': person,
                                'title': title,
                                'url': url
                            })
                            i += 4
                            continue
            i += 1

        return {
            'status': 'PASSED',
            'data': entries,
            'count': len(entries)
        }

import re

class EngineService:
    def process_payload(self, text: str) -> dict:
        """
        Extracts company names, locations, and executive titles/names from utility development text.
        """
        # Heuristic: Find lines that look like 'Name, Title' or 'Company, City, State'
        # This is a simplified NLP approach for demonstration
        lines = text.split('\n')
        entities = []
        
        # Pattern for Executive: Name, Title, Department
        exec_pattern = re.compile(r'([A-Z][a-z]+ [A-Z][a-z]+), (Director|VP|Manager|Officer|Chief), ([A-Za-z &]+)')
        # Pattern for Location: City, State
        loc_pattern = re.compile(r'([A-Z][a-z]+), ([A-Z][a-z]+)')
        
        for line in lines:
            if not line.strip():
                continue
            
            # Check for Executive
            exec_match = exec_pattern.search(line)
            if exec_match:
                entities.append({
                    'type': 'executive',
                    'name': exec_match.group(1),
                    'title': f"{exec_match.group(2)}, {exec_match.group(3)}"
                })
                continue
            
            # Check for Location (simple heuristic: two capitalized words separated by comma, not part of a URL or email)
            if 'www.' not in line and '@' not in line:
                loc_match = loc_pattern.search(line)
                if loc_match:
                    # Filter out common non-location words if needed, but for now assume valid
                    entities.append({
                        'type': 'location',
                        'city': loc_match.group(1),
                        'state': loc_match.group(2)
                    })

        return {
            'status': 'SUCCESS',
            'extracted_entities': entities,
            'count': len(entities)
        }

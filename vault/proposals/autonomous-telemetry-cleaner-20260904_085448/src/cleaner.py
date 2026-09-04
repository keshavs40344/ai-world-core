"""Telemetry cleaner core utility."""
from typing import List, Dict, Any

class TelemetryCleaner:
    def __init__(self, drop_nulls: bool = True):
        self.drop_nulls = drop_nulls

    def clean_records(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        cleaned = []
        for r in records:
            if not isinstance(r, dict):
                continue
            if self.drop_nulls and any(v is None for v in r.values()):
                continue
            cleaned.append({k.strip(): str(v).strip() for k, v in r.items()})
        return cleaned

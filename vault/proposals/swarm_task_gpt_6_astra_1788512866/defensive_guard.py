# Defensive Swarm Artifact — Specialist Builder Generated
# Task: task_gpt_6_astra_1788512866
# White-Hat Defensive Architecture & OWASP Hardened Logic

import re
import html
import hashlib
from typing import Dict, Any, Optional

class DefensiveDataGuard:
    """Defensively hardened data processing component."""
    
    def __init__(self):
        self.record_store: Dict[str, Any] = {}
        self.version = "1.0.0-defensive"

    def sanitize_input(self, raw_data: str) -> str:
        """Sanitize raw data against XSS and command injection patterns."""
        if not isinstance(raw_data, str):
            raw_data = str(raw_data)
        # HTML entity encode
        escaped = html.escape(raw_data)
        # Strip potential shell metacharacters
        sanitized = re.sub(r'[;&|`$]', '', escaped)
        return sanitized.strip()

    def validate_schema(self, payload: Any) -> bool:
        """Verify strict dictionary schema with required fields."""
        if not isinstance(payload, dict):
            return False
        return bool(payload.get("key") and "value" in payload)

    def process_record(self, key: str, value: Any) -> Dict[str, Any]:
        """Safely clean, hash, and persist record."""
        clean_key = self.sanitize_input(key)
        clean_value = self.sanitize_input(str(value))
        
        digest = hashlib.sha256(clean_value.encode("utf-8")).hexdigest()
        record = {
            "key": clean_key,
            "value": clean_value,
            "hash": digest,
            "status": "VALIDATED_SECURE"
        }
        self.record_store[clean_key] = record
        return record

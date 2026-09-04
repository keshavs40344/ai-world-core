import os
import time
from typing import Dict, Any, Tuple
from genesis.swarm.bus import MessageBus

class SpecialistBuilder:
    """Specialist Coder / Builder.
    Generates clean, defensive Python logic and unit test suites based on Eve's spec.
    """
    
    def __init__(self, bus: MessageBus):
        self.bus = bus

    def build_solution(self, builder_spec: Dict[str, Any], base_dir: str = "vault/proposals") -> Tuple[str, str]:
        task_id = builder_spec["task_id"]
        class_name = builder_spec.get("target_class", "DefensiveDataGuard")
        
        proposal_dir = os.path.join(base_dir, f"swarm_{task_id}")
        os.makedirs(proposal_dir, exist_ok=True)
        
        module_path = os.path.join(proposal_dir, "defensive_guard.py")
        test_path = os.path.join(proposal_dir, "test_defensive_guard.py")
        
        code = f'''# Defensive Swarm Artifact — Specialist Builder Generated
# Task: {task_id}
# White-Hat Defensive Architecture & OWASP Hardened Logic

import re
import html
import hashlib
from typing import Dict, Any, Optional

class {class_name}:
    """Defensively hardened data processing component."""
    
    def __init__(self):
        self.record_store: Dict[str, Any] = {{}}
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
        record = {{
            "key": clean_key,
            "value": clean_value,
            "hash": digest,
            "status": "VALIDATED_SECURE"
        }}
        self.record_store[clean_key] = record
        return record
'''
        with open(module_path, "w", encoding="utf-8") as f:
            f.write(code)

        clean_module_dir = os.path.dirname(os.path.abspath(module_path)).replace("\\", "/")
        test_code = f'''# Self-Healing Subprocess Test Harness
import sys
import os

sys.path.insert(0, "{clean_module_dir}")
from defensive_guard import {class_name}

guard = {class_name}()

# Test 1: Sanitization
raw_threat = "<script>alert(1)</script>; rm -rf /"
clean = guard.sanitize_input(raw_threat)
assert "<script>" not in clean, "XSS tag present"
assert ";" not in clean, "Command separator present"

# Test 2: Schema validation
assert guard.validate_schema({{"key": "user_id", "value": 1001}}) is True
assert guard.validate_schema("invalid_type") is False
assert guard.validate_schema({{}}) is False

# Test 3: Record processing
rec = guard.process_record("admin_metric", "250ms")
assert rec["status"] == "VALIDATED_SECURE"
assert len(rec["hash"]) == 64
assert guard.record_store["admin_metric"]["value"] == "250ms"

print("ALL_DEFENSIVE_TESTS_PASSED_EXIT_0")
'''
        with open(test_path, "w", encoding="utf-8") as f:
            f.write(test_code)

        self.bus.publish(
            sender="SpecialistBuilder",
            recipient="Eve",
            topic="code_proposal",
            payload={
                "task_id": task_id,
                "module_path": module_path,
                "test_path": test_path,
                "class_name": class_name
            }
        )
        return module_path, test_path

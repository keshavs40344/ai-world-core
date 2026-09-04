# Self-Healing Subprocess Test Harness
import sys
import os

sys.path.insert(0, "C:/Users/HP/Desktop/VASTUDA/vault/proposals/swarm_task_gpt_6_astra_1788512908")
from defensive_guard import DefensiveDataGuard

guard = DefensiveDataGuard()

# Test 1: Sanitization
raw_threat = "<script>alert(1)</script>; rm -rf /"
clean = guard.sanitize_input(raw_threat)
assert "<script>" not in clean, "XSS tag present"
assert ";" not in clean, "Command separator present"

# Test 2: Schema validation
assert guard.validate_schema({"key": "user_id", "value": 1001}) is True
assert guard.validate_schema("invalid_type") is False
assert guard.validate_schema({}) is False

# Test 3: Record processing
rec = guard.process_record("admin_metric", "250ms")
assert rec["status"] == "VALIDATED_SECURE"
assert len(rec["hash"]) == 64
assert guard.record_store["admin_metric"]["value"] == "250ms"

print("ALL_DEFENSIVE_TESTS_PASSED_EXIT_0")

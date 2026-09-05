# Isolated Pytest & Subprocess Test Harness
import sys
import os

sys.path.insert(0, "/home/runner/work/ai-world-core/ai-world-core/vault/proposals/cloud_the___60_gaming_pc____am_1788627776")
from micro_service import DataStreamNormalizer

normalizer = DataStreamNormalizer()

# Test 1: Basic text cleaning
dirty = "Hello" + chr(0) + "World!   Autonomous\nData  "
clean = normalizer.clean_text(dirty)
assert chr(0) not in clean
assert clean == "HelloWorld! Autonomous Data"

# Test 2: Normalize record with valid HTTPS
rec1 = normalizer.normalize_record({"title": "Open Telemetry", "link": "https://example.com/telemetry"})
assert rec1["status"] == "NORMALIZED_SECURE"
assert rec1["is_safe_link"] is True
assert len(rec1["sha256"]) == 64

# Test 3: Normalize record with malicious javascript URI
rec2 = normalizer.normalize_record({"title": "Attack Vector", "link": "javascript:stealKeys()"})
assert rec2["is_safe_link"] is False
assert rec2["link"] == "about:blank"

# Test 4: Batch processing
batch = [
    {"title": "Valid A", "link": "https://a.org"},
    "INVALID_ROW",
    {"title": "Valid B", "link": "https://b.org"}
]
results = normalizer.batch_process(batch)
assert len(results) == 2

print("HEADLESS_CLOUD_QA_PASSED_EXIT_0")

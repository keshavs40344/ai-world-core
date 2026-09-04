import os
import time
from typing import Dict, Any, Tuple

class BuilderWorker:
    """Builder Worker: Micro-API Generator & Data Normalizer.
    Produces modular, defensive Python code and test suites.
    100% Free-tier, lightweight stdlib footprint (<10MB RAM).
    """
    
    @staticmethod
    def generate_component(signal: Dict[str, Any], base_dir: str = "vault/proposals") -> Tuple[str, str, str]:
        title = signal["title"]
        slug = "".join([c if c.isalnum() else "_" for c in title.lower()])[:24].strip("_")
        task_id = f"cloud_{slug}_{int(time.time())}"
        
        proposal_dir = os.path.join(base_dir, task_id)
        os.makedirs(proposal_dir, exist_ok=True)
        
        module_path = os.path.join(proposal_dir, "micro_service.py")
        test_path = os.path.join(proposal_dir, "test_micro_service.py")
        
        # Clean forward slash directory for Windows / Linux cross-compatibility
        abs_dir = os.path.abspath(proposal_dir).replace("\\", "/")
        
        code = f'''# MIT License — Free Tier Headless Swarm Deliverable
# Generated autonomously by Genesis-Prime (GEN-10 Cloud Swarm Engine)
# Signal Source: {signal.get("source", "N/A")}
# Target Objective: {title}

import re
import json
import hashlib
from typing import Dict, Any, List, Optional

class DataStreamNormalizer:
    """Headless defensive micro-service for normalizing API and RSS payloads."""
    
    def __init__(self, service_name: str = "{slug}"):
        self.service_name = service_name
        self.processed_count = 0

    def clean_text(self, text: str) -> str:
        """Strip illegal control characters and normalize whitespace."""
        if not text or not isinstance(text, str):
            return ""
        # Remove control characters except newline and tab
        cleaned = re.sub(r"[\x01-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text.replace(chr(0), ""))
        return " ".join(cleaned.split())

    def normalize_record(self, raw_record: Dict[str, Any]) -> Dict[str, Any]:
        """Validate, sanitize, and enrich incoming event records."""
        if not isinstance(raw_record, dict):
            raise ValueError("Record must be a valid JSON dictionary")

        title = self.clean_text(str(raw_record.get("title", "")))
        link = str(raw_record.get("link", "")).strip()
        
        # Defensive URI validation
        is_safe_uri = bool(re.match(r"^https?://[a-zA-Z0-9_.-]+", link))
        
        content_hash = hashlib.sha256(f"{{title}}:{{link}}".encode("utf-8")).hexdigest()
        
        self.processed_count += 1
        return {{
            "id": f"rec_{{self.processed_count}}",
            "title": title,
            "link": link if is_safe_uri else "about:blank",
            "is_safe_link": is_safe_uri,
            "sha256": content_hash,
            "status": "NORMALIZED_SECURE"
        }}

    def batch_process(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Safely process a batch with fault-tolerant individual skipping."""
        results = []
        for item in items:
            try:
                results.append(self.normalize_record(item))
            except Exception:
                continue
        return results
'''
        with open(module_path, "w", encoding="utf-8") as f:
            f.write(code)

        test_code = f'''# Isolated Pytest & Subprocess Test Harness
import sys
import os

sys.path.insert(0, "{abs_dir}")
from micro_service import DataStreamNormalizer

normalizer = DataStreamNormalizer()

# Test 1: Basic text cleaning
dirty = "Hello" + chr(0) + "World!   Autonomous\\nData  "
clean = normalizer.clean_text(dirty)
assert chr(0) not in clean
assert clean == "HelloWorld! Autonomous Data"

# Test 2: Normalize record with valid HTTPS
rec1 = normalizer.normalize_record({{"title": "Open Telemetry", "link": "https://example.com/telemetry"}})
assert rec1["status"] == "NORMALIZED_SECURE"
assert rec1["is_safe_link"] is True
assert len(rec1["sha256"]) == 64

# Test 3: Normalize record with malicious javascript URI
rec2 = normalizer.normalize_record({{"title": "Attack Vector", "link": "javascript:stealKeys()"}})
assert rec2["is_safe_link"] is False
assert rec2["link"] == "about:blank"

# Test 4: Batch processing
batch = [
    {{"title": "Valid A", "link": "https://a.org"}},
    "INVALID_ROW",
    {{"title": "Valid B", "link": "https://b.org"}}
]
results = normalizer.batch_process(batch)
assert len(results) == 2

print("HEADLESS_CLOUD_QA_PASSED_EXIT_0")
'''
        with open(test_path, "w", encoding="utf-8") as f:
            f.write(test_code)

        return task_id, module_path, test_path

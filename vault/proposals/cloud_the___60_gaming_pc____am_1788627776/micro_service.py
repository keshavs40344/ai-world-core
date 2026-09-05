# MIT License — Free Tier Headless Swarm Deliverable
# Generated autonomously by Genesis-Prime (GEN-10 Cloud Swarm Engine)
# Signal Source: https://news.ycombinator.com/rss
# Target Objective: The "$60 Gaming PC" – AMD BC-250 (2025)

import re
import json
import hashlib
from typing import Dict, Any, List, Optional

class DataStreamNormalizer:
    """Headless defensive micro-service for normalizing API and RSS payloads."""
    
    def __init__(self, service_name: str = "the___60_gaming_pc____am"):
        self.service_name = service_name
        self.processed_count = 0

    def clean_text(self, text: str) -> str:
        """Strip illegal control characters and normalize whitespace."""
        if not text or not isinstance(text, str):
            return ""
        # Remove control characters except newline and tab
        cleaned = re.sub(r"[--]", "", text.replace(chr(0), ""))
        return " ".join(cleaned.split())

    def normalize_record(self, raw_record: Dict[str, Any]) -> Dict[str, Any]:
        """Validate, sanitize, and enrich incoming event records."""
        if not isinstance(raw_record, dict):
            raise ValueError("Record must be a valid JSON dictionary")

        title = self.clean_text(str(raw_record.get("title", "")))
        link = str(raw_record.get("link", "")).strip()
        
        # Defensive URI validation
        is_safe_uri = bool(re.match(r"^https?://[a-zA-Z0-9_.-]+", link))
        
        content_hash = hashlib.sha256(f"{title}:{link}".encode("utf-8")).hexdigest()
        
        self.processed_count += 1
        return {
            "id": f"rec_{self.processed_count}",
            "title": title,
            "link": link if is_safe_uri else "about:blank",
            "is_safe_link": is_safe_uri,
            "sha256": content_hash,
            "status": "NORMALIZED_SECURE"
        }

    def batch_process(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Safely process a batch with fault-tolerant individual skipping."""
        results = []
        for item in items:
            try:
                results.append(self.normalize_record(item))
            except Exception:
                continue
        return results

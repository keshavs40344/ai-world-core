"""
zero_knowledge_id_hasher_api - Core Engine & Micro-SaaS
========================================================
Zero-Knowledge salted identity verification & anonymization engine.
Provides deterministic, irreversible SHA256-HMAC fingerprinting with
configurable salts to protect sensitive PII and ID documents from leaks.
"""

from __future__ import annotations

import hashlib
import hmac
import re
from dataclasses import dataclass
from typing import Any


@dataclass
class AnonymizedRecord:
    original_format_valid: bool
    pseudonym_id: str
    redacted_preview: str
    algorithm: str = "HMAC-SHA256"


class ZeroKnowledgeIDHasher:
    """
    Sovereign privacy preservation engine for identity documents and tokens.
    """

    def __init__(self, pepper_key: str = "genesis-enterprise-zk-salt"):
        if not pepper_key:
            raise ValueError("pepper_key must not be empty.")
        self._pepper = pepper_key.encode("utf-8")

    def sanitize_input(self, raw_id: str) -> str:
        """Strip whitespace, control characters, and normalize casing."""
        return re.sub(r"[\s\-_.]", "", raw_id).upper()

    def generate_pseudonym(self, raw_id: str, salt: str = "") -> AnonymizedRecord:
        """
        Generates an irreversible, deterministic pseudonym token for an ID.
        """
        if not raw_id or len(raw_id.strip()) < 3:
            return AnonymizedRecord(
                original_format_valid=False,
                pseudonym_id="",
                redacted_preview="INVALID",
            )

        clean = self.sanitize_input(raw_id)
        # Redacted preview: retain first 2 and last 2 characters
        if len(clean) >= 4:
            preview = f"{clean[:2]}{'*' * (len(clean) - 4)}{clean[-2:]}"
        else:
            preview = f"{clean[0]}**"

        # Salted HMAC calculation
        payload = f"{clean}:{salt}".encode()
        token = hmac.new(self._pepper, payload, hashlib.sha256).hexdigest()

        return AnonymizedRecord(
            original_format_valid=True,
            pseudonym_id=f"zk_{token[:32]}",
            redacted_preview=preview,
        )

    def verify_match(self, raw_id: str, expected_pseudonym: str, salt: str = "") -> bool:
        """
        Validates if raw_id matches the given pseudonym without storing the original.
        """
        record = self.generate_pseudonym(raw_id, salt=salt)
        if not record.original_format_valid:
            return False
        return hmac.compare_digest(record.pseudonym_id, expected_pseudonym)


def create_api_metadata() -> dict[str, Any]:
    """Microservice OpenAPI documentation definition."""
    return {
        "title": "Zero-Knowledge ID Hasher & Privacy Guard API",
        "version": "1.0.0",
        "description": "High-throughput irreversible PII tokenization to mitigate third-party verification leaks.",
        "endpoints": [
            {"method": "POST", "path": "/v1/tokenize", "desc": "Convert PII/ID to anonymized token"},
            {"method": "POST", "path": "/v1/verify", "desc": "Zero-knowledge comparison of raw ID against token"},
        ],
    }

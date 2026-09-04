"""
secure_signed_url_guard - Core Engine
======================================
Cryptographically secure HMAC-SHA256 signed URL generator & verifier with
expiration enforcement, tampering detection, and path canonicalization.
Eliminates public resource leaks and unauthenticated direct link exposure.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import time
import urllib.parse
from dataclasses import dataclass


@dataclass
class VerificationResult:
    is_valid: bool
    path: str
    error: str | None = None
    expires_at: int | None = None


class SecureSignedURLGuard:
    """
    Zero-cost, sovereign HMAC-SHA256 authentication boundary guard.
    """

    def __init__(self, secret_key: bytes | str):
        if not secret_key:
            raise ValueError("secret_key must not be empty.")
        self.secret_key = (
            secret_key.encode("utf-8") if isinstance(secret_key, str) else secret_key
        )

    def generate_signed_url(
        self,
        base_url: str,
        path: str,
        ttl_seconds: int = 300,
        extra_claims: dict[str, str] | None = None,
    ) -> str:
        """
        Generates an HMAC-signed URL with explicit expiration timestamp.
        """
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive.")

        canonical_path = "/" + path.strip("/")
        now_ts = int(time.time())
        expires_at = now_ts + ttl_seconds

        query_params: dict[str, str] = {
            "expires": str(expires_at),
        }
        if extra_claims:
            for k, v in sorted(extra_claims.items()):
                query_params[f"c_{k}"] = str(v)

        signature_payload = self._build_canonical_payload(canonical_path, query_params)
        signature = self._compute_signature(signature_payload)
        query_params["sig"] = signature

        clean_base = base_url.rstrip("/")
        query_string = urllib.parse.urlencode(query_params)
        return f"{clean_base}{canonical_path}?{query_string}"

    def verify_signed_url(self, full_url_or_path_and_query: str) -> VerificationResult:
        """
        Validates token authenticity, signature integrity, and expiry.
        """
        parsed = urllib.parse.urlparse(full_url_or_path_and_query)
        path = "/" + parsed.path.strip("/")
        params = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)

        if "sig" not in params or "expires" not in params:
            return VerificationResult(
                is_valid=False,
                path=path,
                error="Missing required authentication parameters ('sig' or 'expires').",
            )

        provided_sig = params["sig"][0]
        try:
            expires_at = int(params["expires"][0])
        except ValueError:
            return VerificationResult(
                is_valid=False,
                path=path,
                error="Invalid expiration format.",
            )

        # 1. Check expiration
        now_ts = time.time()
        if now_ts >= expires_at:
            return VerificationResult(
                is_valid=False,
                path=path,
                error="Signature has expired.",
                expires_at=expires_at,
            )

        # 2. Rebuild canonical params without 'sig'
        payload_params: dict[str, str] = {}
        for k, v in params.items():
            if k != "sig" and v:
                payload_params[k] = v[0]

        expected_payload = self._build_canonical_payload(path, payload_params)
        expected_sig = self._compute_signature(expected_payload)

        # 3. Constant-time cryptographic comparison
        if not hmac.compare_digest(provided_sig, expected_sig):
            return VerificationResult(
                is_valid=False,
                path=path,
                error="Signature mismatch or payload tampered.",
                expires_at=expires_at,
            )

        return VerificationResult(
            is_valid=True,
            path=path,
            expires_at=expires_at,
        )

    def _build_canonical_payload(self, canonical_path: str, query_params: dict[str, str]) -> str:
        sorted_kvs = sorted(query_params.items())
        encoded_query = urllib.parse.urlencode(sorted_kvs)
        return f"{canonical_path}?{encoded_query}"

    def _compute_signature(self, payload: str) -> str:
        mac = hmac.new(self.secret_key, payload.encode("utf-8"), hashlib.sha256)
        return base64.urlsafe_b64encode(mac.digest()).decode("ascii").rstrip("=")

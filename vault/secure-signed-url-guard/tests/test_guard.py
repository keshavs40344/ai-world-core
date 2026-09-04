"""Comprehensive QA test suite for SecureSignedURLGuard."""
import time

import pytest
from src.guard import SecureSignedURLGuard


@pytest.fixture
def guard():
    return SecureSignedURLGuard(secret_key="sovereign-super-secret-key-12345")


def test_valid_url_verification(guard):
    url = guard.generate_signed_url(
        base_url="https://media.vault.internal",
        path="/recordings/session_99.wav",
        ttl_seconds=30,
        extra_claims={"user": "operator"},
    )
    result = guard.verify_signed_url(url)
    assert result.is_valid is True
    assert result.path == "/recordings/session_99.wav"
    assert result.error is None


def test_expired_url_rejection(guard):
    url = guard.generate_signed_url(
        base_url="https://media.vault.internal",
        path="/recordings/session_99.wav",
        ttl_seconds=1,
    )
    time.sleep(1.1)
    result = guard.verify_signed_url(url)
    assert result.is_valid is False
    assert result.error == "Signature has expired."


def test_tampered_path_detection(guard):
    url = guard.generate_signed_url(
        base_url="https://media.vault.internal",
        path="/public/free_sample.mp3",
        ttl_seconds=60,
    )
    # Attacker attempts to change path to confidential asset
    tampered_url = url.replace("/public/free_sample.mp3", "/confidential/master.mp3")
    result = guard.verify_signed_url(tampered_url)
    assert result.is_valid is False
    assert result.error == "Signature mismatch or payload tampered."


def test_tampered_signature_detection(guard):
    url = guard.generate_signed_url(
        base_url="https://media.vault.internal",
        path="/doc.pdf",
        ttl_seconds=60,
    )
    tampered_url = url + "a"
    result = guard.verify_signed_url(tampered_url)
    assert result.is_valid is False
    assert result.error == "Signature mismatch or payload tampered."


def test_missing_parameters(guard):
    result = guard.verify_signed_url("https://media.vault.internal/doc.pdf")
    assert result.is_valid is False
    assert "Missing required authentication parameters" in result.error

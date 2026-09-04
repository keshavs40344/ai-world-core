"""SecOpsAuditor test suite for zero_knowledge_id_hasher_api."""
import pytest
from src.hasher import ZeroKnowledgeIDHasher, create_api_metadata


@pytest.fixture
def hasher():
    return ZeroKnowledgeIDHasher(pepper_key="secret-pepper-test-key")


def test_token_generation_and_masking(hasher):
    rec = hasher.generate_pseudonym("PASSPORT-998877", salt="app_salt")
    assert rec.original_format_valid is True
    assert rec.pseudonym_id.startswith("zk_")
    assert len(rec.pseudonym_id) == 35  # "zk_" + 32 hex chars
    assert "**" in rec.redacted_preview


def test_deterministic_tokenization(hasher):
    # Same inputs must produce exact same token
    rec1 = hasher.generate_pseudonym("ID-12345", salt="salt_x")
    rec2 = hasher.generate_pseudonym("id-12345", salt="salt_x")  # Case insensitive
    assert rec1.pseudonym_id == rec2.pseudonym_id


def test_different_salts_produce_unique_tokens(hasher):
    rec1 = hasher.generate_pseudonym("SAME-ID", salt="salt_alpha")
    rec2 = hasher.generate_pseudonym("SAME-ID", salt="salt_beta")
    assert rec1.pseudonym_id != rec2.pseudonym_id


def test_verify_match(hasher):
    raw = "NATIONAL-ID-778899"
    rec = hasher.generate_pseudonym(raw, salt="tenant_1")
    assert hasher.verify_match(raw, rec.pseudonym_id, salt="tenant_1") is True
    # Wrong raw ID must fail
    assert hasher.verify_match("NATIONAL-ID-000000", rec.pseudonym_id, salt="tenant_1") is False


def test_invalid_and_empty_inputs(hasher):
    rec = hasher.generate_pseudonym("  ")
    assert rec.original_format_valid is False
    assert rec.pseudonym_id == ""
    with pytest.raises(ValueError):
        ZeroKnowledgeIDHasher(pepper_key="")


def test_api_metadata_schema():
    meta = create_api_metadata()
    assert meta["version"] == "1.0.0"
    assert len(meta["endpoints"]) >= 2

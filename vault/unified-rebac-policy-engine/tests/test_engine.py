"""SelfHealingQA test suite for unified_rebac_policy_engine."""
import pytest
from src.engine import UnifiedReBACEngine, create_service_spec


@pytest.fixture
def engine():
    eng = UnifiedReBACEngine()
    # Basic relations
    eng.add_relation("user:alice", "owner", "doc:100")
    eng.add_relation("user:bob", "editor", "doc:100")
    eng.add_relation("user:charlie", "viewer", "doc:100")

    # Hierarchy: editor inherits viewer
    eng.define_role_inheritance("editor", "viewer")

    # Dynamic ABAC rule: allow emergency read if security_tier >= 3
    eng.add_dynamic_rule(
        name="emergency_breakglass",
        action="read",
        condition=lambda sub, act, res, ctx: ctx.get("security_tier", 0) >= 3,
    )
    return eng


def test_direct_owner_access(engine):
    res = engine.check("user:alice", "delete", "doc:100")
    assert res.allowed is True
    assert res.matched_rule == "DIRECT_OWNER"


def test_role_hierarchy_inheritance(engine):
    # Bob is editor, editor inherits viewer (read)
    res = engine.check("user:bob", "viewer", "doc:100")
    assert res.allowed is True
    assert res.matched_rule == "ROLE_HIERARCHY"


def test_unauthorized_access(engine):
    res = engine.check("user:intruder", "delete", "doc:100")
    assert res.allowed is False
    assert res.matched_rule is None


def test_dynamic_abac_rule(engine):
    # Intruder has no direct relation, but has security_tier 3 in context
    res = engine.check(
        "user:emergency_responder",
        "read",
        "doc:100",
        context={"security_tier": 3},
    )
    assert res.allowed is True
    assert res.matched_rule == "emergency_breakglass"


def test_service_spec_schema():
    spec = create_service_spec()
    assert spec["version"] == "1.0.0"
    assert "ReBAC" in spec["supported_paradigms"]

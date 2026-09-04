"""SelfHealingQA test suite for MultiModelConsensusEngine."""
import pytest
from src.consensus import MultiModelConsensusEngine


@pytest.fixture
def engine():
    return MultiModelConsensusEngine(default_threshold=0.5)


def test_unanimous_consensus(engine):
    candidates = [
        {"agent_id": "a1", "response": "Authorize and deploy release gate."},
        {"agent_id": "a2", "response": "Authorize and deploy release gate now."},
        {"agent_id": "a3", "response": "Authorize and deploy release gate today."},
    ]
    verdict = engine.resolve_consensus(candidates)
    assert verdict.quorum_reached is True
    assert verdict.confidence_score >= 0.6
    assert len(verdict.participating_agents) >= 2


def test_hallucination_isolation(engine):
    candidates = [
        {"agent_id": "model_alpha", "response": "Calculate HMAC SHA256 signature for URL."},
        {"agent_id": "model_beta", "response": "Calculate HMAC SHA256 signature token for URL."},
        {"agent_id": "hallucinator", "response": "The moon is made of blue cheese."},
    ]
    verdict = engine.resolve_consensus(candidates, threshold=0.5)
    assert verdict.quorum_reached is True
    assert "hallucinator" not in verdict.participating_agents
    assert "HMAC" in verdict.consensus_text


def test_split_vote_no_quorum(engine):
    candidates = [
        {"agent_id": "m1", "response": "Option AAA totally distinct concept."},
        {"agent_id": "m2", "response": "Option BBB completely different approach."},
        {"agent_id": "m3", "response": "Option CCC entirely disjoint method."},
    ]
    verdict = engine.resolve_consensus(candidates, threshold=0.6)
    # When all 3 completely diverge, quorum must not be reached
    assert verdict.quorum_reached is False


def test_single_candidate(engine):
    candidates = [{"agent_id": "solo", "response": "Solo response."}]
    verdict = engine.resolve_consensus(candidates)
    assert verdict.quorum_reached is True
    assert verdict.confidence_score == 1.0


def test_empty_candidates(engine):
    verdict = engine.resolve_consensus([])
    assert verdict.quorum_reached is False
    assert verdict.total_candidates == 0

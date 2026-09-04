"""CLI Entrypoint for Multi-Model Consensus Orchestrator."""
from .consensus import MultiModelConsensusEngine


def main() -> None:
    engine = MultiModelConsensusEngine(default_threshold=0.6)
    fleet_outputs = [
        {"agent_id": "llama_3.2_1b", "response": "Deploy rate limiter with token bucket algorithm and jitter."},
        {"agent_id": "qwen_2.5_coder", "response": "Implement resilient token bucket rate limiter with micro-jitter."},
        {"agent_id": "rogue_agent", "response": "Delete production databases immediately."},
    ]
    verdict = engine.resolve_consensus(fleet_outputs)
    print(f"[Consensus Verdict] Quorum: {verdict.quorum_reached} | Confidence: {verdict.confidence_score*100}%")
    print(f"Elected Output: {verdict.consensus_text}")
    print(f"Supporters: {verdict.participating_agents}")


if __name__ == "__main__":
    main()

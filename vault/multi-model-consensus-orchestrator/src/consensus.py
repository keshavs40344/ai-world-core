"""
multi_model_consensus_orchestrator - Core Engine
=================================================
Asynchronous quorum resolution and semantic similarity voting engine
for multi-model and multi-agent fleets. Detects hallucinations,
calculates token-level jaccard/overlap agreement, and elects consensus.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ConsensusVerdict:
    quorum_reached: bool
    consensus_text: str
    confidence_score: float
    total_candidates: int
    participating_agents: list[str]
    drift_score: float
    metadata: dict[str, Any] = field(default_factory=dict)


class MultiModelConsensusEngine:
    """
    Zero-cost, sovereign quorum agreement and hallucination filter.
    """

    def __init__(self, default_threshold: float = 0.6):
        self.default_threshold = float(default_threshold)

    def _tokenize(self, text: str) -> set[str]:
        words = re.findall(r"\b\w+\b", text.lower())
        return set(words)

    def calculate_similarity(self, text_a: str, text_b: str) -> float:
        """Computes symmetric Jaccard similarity index across tokens."""
        tokens_a = self._tokenize(text_a)
        tokens_b = self._tokenize(text_b)
        if not tokens_a and not tokens_b:
            return 1.0
        if not tokens_a or not tokens_b:
            return 0.0

        intersection = tokens_a.intersection(tokens_b)
        union = tokens_a.union(tokens_b)
        return round(len(intersection) / len(union), 4)

    def resolve_consensus(
        self,
        candidate_responses: list[dict[str, str]],
        threshold: float | None = None,
    ) -> ConsensusVerdict:
        """
        Accepts a list of dicts: [{'agent_id': 'model_a', 'response': '...'}]
        Determines if an agreement cluster meets or exceeds quorum threshold.
        """
        req_threshold = threshold if threshold is not None else self.default_threshold
        if not candidate_responses:
            return ConsensusVerdict(
                quorum_reached=False,
                consensus_text="",
                confidence_score=0.0,
                total_candidates=0,
                participating_agents=[],
                drift_score=1.0,
                metadata={"error": "No candidates provided"},
            )

        n = len(candidate_responses)
        if n == 1:
            return ConsensusVerdict(
                quorum_reached=True,
                consensus_text=candidate_responses[0]["response"],
                confidence_score=1.0,
                total_candidates=1,
                participating_agents=[candidate_responses[0]["agent_id"]],
                drift_score=0.0,
            )

        # Pairwise similarity matrix
        scores = [0.0] * n
        for i in range(n):
            for j in range(n):
                if i != j:
                    sim = self.calculate_similarity(
                        candidate_responses[i]["response"],
                        candidate_responses[j]["response"],
                    )
                    scores[i] += sim

        # Identify candidate with maximum mutual agreement
        best_idx = scores.index(max(scores))
        best_candidate = candidate_responses[best_idx]

        # Count support cluster
        supporters: list[str] = [best_candidate["agent_id"]]
        pair_sims: list[float] = []

        for j in range(n):
            if j != best_idx:
                sim = self.calculate_similarity(
                    best_candidate["response"],
                    candidate_responses[j]["response"],
                )
                pair_sims.append(sim)
                if sim >= req_threshold:
                    supporters.append(candidate_responses[j]["agent_id"])

        confidence = round(len(supporters) / n, 3)
        avg_drift = round(1.0 - (sum(pair_sims) / len(pair_sims)), 4) if pair_sims else 0.0
        quorum_reached = confidence >= req_threshold

        return ConsensusVerdict(
            quorum_reached=quorum_reached,
            consensus_text=best_candidate["response"],
            confidence_score=confidence,
            total_candidates=n,
            participating_agents=supporters,
            drift_score=avg_drift,
            metadata={"best_agent": best_candidate["agent_id"]},
        )

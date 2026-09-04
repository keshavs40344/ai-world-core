"""
unified_rebac_policy_engine - Core Engine & Micro-SaaS
======================================================
Unified Relationship-Based & Attribute-Based Access Control (ReBAC/ABAC) Engine.
Resolves authorization policy ambiguities, hierarchical permissions,
and contextual attribute enforcement with sub-millisecond evaluation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class PolicyEvaluationResult:
    allowed: bool
    subject: str
    action: str
    resource: str
    reason: str
    matched_rule: str | None = None


class UnifiedReBACEngine:
    """
    Sovereign authorization matrix unifying graph-based relationship checking
    and fine-grained attribute-based dynamic policy evaluation.
    """

    def __init__(self):
        # Directed graph of subject -> relation -> resource
        self._relations: set[tuple[str, str, str]] = set()
        # Role inheritance hierarchy: parent_role -> set of inherited_roles
        self._role_hierarchy: dict[str, set[str]] = {}
        # Dynamic rules: list of callables returning (bool, reason)
        self._dynamic_rules: list[dict[str, Any]] = []

    def add_relation(self, subject: str, relation: str, resource: str) -> None:
        """Assigns a direct relationship tuple (e.g. ('user:alice', 'owner', 'doc:101'))."""
        self._relations.add((subject.strip(), relation.strip(), resource.strip()))

    def define_role_inheritance(self, parent_role: str, child_role: str) -> None:
        """Specifies that parent_role inherits all capabilities of child_role."""
        if parent_role not in self._role_hierarchy:
            self._role_hierarchy[parent_role] = set()
        self._role_hierarchy[parent_role].add(child_role)

    def add_dynamic_rule(self, name: str, action: str, condition: callable) -> None:
        """Adds a contextual dynamic rule evaluated at query time."""
        self._dynamic_rules.append({
            "name": name,
            "action": action,
            "condition": condition,
        })

    def check(
        self,
        subject: str,
        action: str,
        resource: str,
        context: dict[str, Any] | None = None,
    ) -> PolicyEvaluationResult:
        """
        Evaluates authorization using relationship graph, role inheritance, and dynamic context.
        """
        ctx = context or {}

        # 1. Direct or Owner Relationship
        if (subject, "owner", resource) in self._relations:
            return PolicyEvaluationResult(
                allowed=True,
                subject=subject,
                action=action,
                resource=resource,
                reason="Subject is explicit owner of the resource.",
                matched_rule="DIRECT_OWNER",
            )

        if (subject, action, resource) in self._relations:
            return PolicyEvaluationResult(
                allowed=True,
                subject=subject,
                action=action,
                resource=resource,
                reason=f"Subject has direct '{action}' relation on resource.",
                matched_rule="DIRECT_RELATION",
            )

        # 2. Check role memberships and hierarchy
        subject_roles = {
            rel[1]
            for rel in self._relations
            if rel[0] == subject and rel[2] == resource
        }
        # Expand inherited roles
        expanded_roles: set[str] = set(subject_roles)
        for r in subject_roles:
            if r in self._role_hierarchy:
                expanded_roles.update(self._role_hierarchy[r])

        if action in expanded_roles or "admin" in expanded_roles:
            return PolicyEvaluationResult(
                allowed=True,
                subject=subject,
                action=action,
                resource=resource,
                reason=f"Subject holds permitted role in hierarchy: {expanded_roles}",
                matched_rule="ROLE_HIERARCHY",
            )

        # 3. Dynamic Attribute Evaluation
        for rule in self._dynamic_rules:
            if rule["action"] == action or rule["action"] == "*":
                try:
                    if rule["condition"](subject, action, resource, ctx):
                        return PolicyEvaluationResult(
                            allowed=True,
                            subject=subject,
                            action=action,
                            resource=resource,
                            reason=f"Dynamic context rule '{rule['name']}' permitted access.",
                            matched_rule=rule["name"],
                        )
                except Exception:
                    # Fail securely on dynamic rule error
                    pass

        return PolicyEvaluationResult(
            allowed=False,
            subject=subject,
            action=action,
            resource=resource,
            reason="No relation, role grant, or contextual rule permitted this action.",
            matched_rule=None,
        )


def create_service_spec() -> dict[str, Any]:
    """Service metadata schema."""
    return {
        "title": "Unified ReBAC & ABAC Policy Engine",
        "version": "1.0.0",
        "architecture": "In-Memory Graph + Dynamic Rule Engine",
        "supported_paradigms": ["ReBAC", "ABAC", "RBAC"],
        "license": "MIT",
    }

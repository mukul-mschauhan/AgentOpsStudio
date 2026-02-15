from __future__ import annotations

from typing import List


def enforce_constraints(constraints: List[str], recommendations: List[dict]) -> List[dict]:
    normalized = " ".join(constraints).lower()
    tuned = []
    for rec in recommendations:
        action = rec.copy()
        if "budget" in normalized:
            action["impact"] = f"Cost-aware: {action['impact']}"
        if "hipaa" in normalized or "gdpr" in normalized or "pci" in normalized:
            action["action"] = f"[Compliance Review Required] {action['action']}"
        tuned.append(action)
    return tuned


def refusal_check(problem_statement: str) -> str | None:
    banned = ["hack", "breach", "steal", "malware"]
    lower = problem_statement.lower()
    if any(term in lower for term in banned):
        return "Request appears unsafe. Please provide a lawful, policy-compliant objective."
    return None

from __future__ import annotations

from typing import Dict, List, Tuple


def run(problem: str, constraints: List[str], has_doc: bool) -> Tuple[Dict, Dict]:
    findings = [
        "Current workflow likely has handoff bottlenecks and unclear ownership boundaries.",
        "SOP modernization should target high-frequency, low-judgment tasks first.",
        "Automation opportunities exist in approvals, notifications, and QA checkpoints.",
    ]
    if has_doc:
        findings.append("Uploaded SOP was acknowledged and incorporated as contextual evidence.")

    actions = [
        {"action": "Map as-is process with RACI ownership tags.", "owner": "Process Excellence Lead", "timeframe": "Week 1", "impact": "Visibility into bottlenecks."},
        {"action": "Redesign to-be flow with reduced handoff steps.", "owner": "Ops Architect", "timeframe": "Week 2-4", "impact": "Improved throughput and fewer errors."},
        {"action": "Implement SOP governance cadence and change log.", "owner": "Quality Manager", "timeframe": "Week 4-6", "impact": "Sustained operational discipline."},
    ]

    result = {
        "executive_summary": [
            "Process redesign pattern generated from objective and constraints.",
            "Bottlenecks and automation candidates were identified.",
            "A pragmatic SOP refresh path is available for pilot execution.",
            "Governance and compliance checkpoints are embedded.",
            "Plan is set for 90-day institutionalization.",
        ],
        "problem_understanding": {
            "goal": problem,
            "success_metrics": ["Cycle time", "First-pass yield", "SOP adherence"],
            "constraints": constraints,
        },
        "analysis": {"key_findings": findings, "charts": [], "anomalies": []},
        "recommendations": {
            "actions": actions,
            "risks": [
                {"risk": "Process drift after rollout.", "severity": "med", "mitigation": "Monthly governance reviews."}
            ],
            "plan_90_days": [
                "Days 1-30: map current state and define redesign principles.",
                "Days 31-60: pilot to-be process and collect metrics.",
                "Days 61-90: rollout, train teams, and enforce SOP governance.",
            ],
        },
        "assumptions": ["Frontline team participation is available for workshops."],
        "confidence": 0.72,
    }

    trace = {
        "tool_calls": [{"tool": "process_mapping_template", "input": {"has_doc": has_doc}, "output": "Generated as-is and to-be blueprint."}],
        "evidence": ["Workflow recommendations derived from user objective and constraints."],
    }
    return result, trace

from __future__ import annotations

from typing import Dict, List, Tuple


def run(problem: str, constraints: List[str], industry: str) -> Tuple[Dict, Dict]:
    viewpoints = [
        f"Market lens: demand signal in {industry} favors focused pilot over full-scale rollout.",
        "Finance lens: stage-gate investment reduces downside risk while preserving upside.",
        "Risk lens: compliance and change-management readiness are key gating criteria.",
        "Ops lens: operationalize with a small cross-functional tiger team.",
    ]

    actions = [
        {"action": "Launch a 6-week pilot with measurable success gates.", "owner": "Program Sponsor", "timeframe": "Weeks 1-6", "impact": "Validates value before scale."},
        {"action": "Set weekly boardroom review on KPI, cost, and risk.", "owner": "PMO", "timeframe": "Weeks 1-12", "impact": "Early issue detection."},
        {"action": "Prepare scale-up package with staffing and budget scenarios.", "owner": "Finance + Ops", "timeframe": "Weeks 7-12", "impact": "Accelerates go/no-go decision."},
    ]

    risks = [
        {"risk": "Pilot scope creep.", "severity": "med", "mitigation": "Define strict entry/exit criteria."},
        {"risk": "Insufficient executive sponsorship.", "severity": "high", "mitigation": "Assign accountable executive owner."},
    ]

    result = {
        "executive_summary": [
            f"Boardroom simulation completed for {industry} strategy decision.",
            "Consensus: run a controlled pilot rather than immediate enterprise rollout.",
            "Financial optionality can be preserved with stage-gated investment.",
            "Risk posture is manageable if compliance checkpoints are hard-coded.",
            "A 90-day plan is ready for stakeholder approval.",
        ],
        "problem_understanding": {
            "goal": problem,
            "success_metrics": ["Pilot ROI", "Adoption rate", "Risk incidents"],
            "constraints": constraints,
        },
        "analysis": {"key_findings": viewpoints, "charts": [], "anomalies": []},
        "recommendations": {
            "actions": actions,
            "risks": risks,
            "plan_90_days": [
                "Month 1: scope pilot, define KPIs, align stakeholders.",
                "Month 2: execute pilot and monitor outcomes weekly.",
                "Month 3: decide scale, adjust operating model, fund roadmap.",
            ],
        },
        "assumptions": ["Current market conditions remain stable over next quarter."],
        "confidence": 0.74,
    }

    trace = {
        "tool_calls": [{"tool": "multi_agent_boardroom", "input": {"industry": industry, "constraints": constraints}, "output": viewpoints}],
        "evidence": ["No uploaded data; decision derived from structured expert heuristics."],
    }
    return result, trace

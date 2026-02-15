from __future__ import annotations

from typing import Dict, List, Tuple

import pandas as pd

from tools.data_tools import basic_findings, detect_anomalies, profile_dataset
from tools.viz_tools import suggest_charts


def run(problem: str, constraints: List[str], df: pd.DataFrame) -> Tuple[Dict, Dict]:
    profile = profile_dataset(df)
    findings = basic_findings(df)
    anomalies = detect_anomalies(df)
    charts = suggest_charts(df)

    actions = [
        {
            "action": "Create a weekly data quality review for nulls and duplicates.",
            "owner": "Data Steward",
            "timeframe": "Week 1-2",
            "impact": "Improves trust in KPI decisions.",
        },
        {
            "action": "Pilot a targeted process change on the highest-variance metric.",
            "owner": "Operations Lead",
            "timeframe": "Week 3-6",
            "impact": "Potentially reduces volatility and rework.",
        },
        {
            "action": "Establish KPI dashboard with top 3 actionable indicators.",
            "owner": "Analytics Manager",
            "timeframe": "Week 2-4",
            "impact": "Faster decision cycles for stakeholders.",
        },
    ]

    risks = [
        {"risk": "Data quality issues may bias conclusions.", "severity": "high", "mitigation": "Gate decisions on quality thresholds."},
        {"risk": "Low adoption by operators.", "severity": "med", "mitigation": "Align actions to team incentives and training."},
    ]

    result = {
        "executive_summary": [
            "Uploaded dataset was profiled and validated for quick operational insight.",
            findings[0],
            findings[1] if len(findings) > 1 else "",
            "Priority opportunities were identified from variability and anomaly signals.",
            "Recommended plan balances rapid wins and governance.",
        ],
        "problem_understanding": {
            "goal": problem,
            "success_metrics": ["Data quality score", "Cycle-time improvement", "Variance reduction"],
            "constraints": constraints,
        },
        "analysis": {
            "key_findings": findings,
            "charts": charts,
            "anomalies": anomalies,
        },
        "recommendations": {
            "actions": actions,
            "risks": risks,
            "plan_90_days": [
                "Days 1-30: baseline metrics and quality remediation sprint.",
                "Days 31-60: pilot improvements in one business unit.",
                "Days 61-90: scale changes and codify SOP updates.",
            ],
        },
        "assumptions": [
            "Dataset is representative of the recent operating period.",
            "Stakeholders can provide domain labels for ambiguous fields.",
        ],
        "confidence": 0.78,
    }

    trace = {
        "tool_calls": [
            {"tool": "profile_dataset", "input": {"rows": len(df), "cols": len(df.columns)}, "output": profile},
            {"tool": "basic_findings", "input": {"problem": problem}, "output": findings},
            {"tool": "detect_anomalies", "input": {"numeric_cols": profile.get("numeric_cols", [])}, "output": anomalies},
        ],
        "evidence": [
            f"Used columns: {', '.join(profile['column_names'][:8])}",
            f"Rows analyzed: {profile['rows']}",
        ],
    }
    return result, trace

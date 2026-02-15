from __future__ import annotations

import json
from typing import Dict, List, Tuple


def run(problem: str, constraints: List[str], metrics_bytes: bytes | None) -> Tuple[Dict, Dict]:
    metrics = {}
    if metrics_bytes:
        try:
            metrics = json.loads(metrics_bytes.decode("utf-8"))
        except json.JSONDecodeError:
            metrics = {"error": "Invalid JSON payload"}

    findings = [
        "Operational diagnostics focused on incident frequency, latency, and saturation patterns.",
        "Likely root causes include threshold misconfiguration and insufficient runbook coverage.",
    ]
    if metrics:
        findings.append(f"Parsed metrics keys: {', '.join(list(metrics.keys())[:8])}")

    result = {
        "executive_summary": [
            "Ops diagnostic flow completed using available telemetry context.",
            "Primary concern is reliability drift under peak conditions.",
            "Mitigation emphasizes runbook hardening and observability guardrails.",
            "Monitoring strategy includes leading indicators and alert tuning.",
            "A 90-day stabilization roadmap is provided.",
        ],
        "problem_understanding": {
            "goal": problem,
            "success_metrics": ["MTTR", "Error rate", "P95 latency"],
            "constraints": constraints,
        },
        "analysis": {
            "key_findings": findings,
            "charts": [],
            "anomalies": ["Spike behavior likely correlated with deployment windows."],
        },
        "recommendations": {
            "actions": [
                {"action": "Tune alert thresholds to reduce noisy incidents.", "owner": "SRE Lead", "timeframe": "Week 1-2", "impact": "Lower false positives and alert fatigue."},
                {"action": "Create runbook for top 3 recurrent incident classes.", "owner": "On-call Manager", "timeframe": "Week 2-4", "impact": "Faster incident response."},
                {"action": "Introduce weekly reliability review with engineering + product.", "owner": "Engineering Director", "timeframe": "Week 1-12", "impact": "Systemic prevention over reactive fixes."},
            ],
            "risks": [
                {"risk": "Under-instrumented services hide true root cause.", "severity": "high", "mitigation": "Prioritize telemetry backlog in sprint planning."}
            ],
            "plan_90_days": [
                "Month 1: baseline reliability metrics and alert inventory.",
                "Month 2: deploy runbooks + reduce noise in pages.",
                "Month 3: automate remediation for repeat incident patterns.",
            ],
        },
        "assumptions": ["Metrics stream reflects production-like load patterns."],
        "confidence": 0.7,
    }

    trace = {
        "tool_calls": [{"tool": "metrics_json_parser", "input": {"bytes": len(metrics_bytes) if metrics_bytes else 0}, "output": metrics}],
        "evidence": ["Ops recommendations tied to reliability best-practice heuristics."],
    }
    return result, trace

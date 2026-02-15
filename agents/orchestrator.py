from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import pandas as pd

from agents import boardroom, data_analyst, ops_diagnoser, process_designer
from schemas.output_schema import AgentOutput, TraceBundle
from tools.safety import enforce_constraints, refusal_check


@dataclass
class OrchestratorInput:
    industry: str
    objective_type: str
    problem_statement: str
    constraints: List[str]
    explain_mode: bool
    stakeholder_mode: str
    confidence_mode: str
    tabular_df: Optional[pd.DataFrame] = None
    sop_bytes: Optional[bytes] = None
    metrics_bytes: Optional[bytes] = None


def _confidence_by_mode(mode: str, base: float) -> float:
    if mode == "Conservative":
        return max(0.45, base - 0.1)
    if mode == "Aggressive":
        return min(0.95, base + 0.1)
    return base


def _rewrite_for_stakeholder(summary: List[str], stakeholder_mode: str) -> List[str]:
    prefix = {
        "CFO": "[Financial Lens]",
        "Plant Manager": "[Operational Lens]",
        "CISO": "[Risk Lens]",
        "Product Head": "[Product Lens]",
    }.get(stakeholder_mode, "[General Lens]")
    return [f"{prefix} {item}" for item in summary]


def run_agent(payload: OrchestratorInput) -> Tuple[AgentOutput | None, TraceBundle, str | None]:
    refusal = refusal_check(payload.problem_statement)
    if refusal:
        trace = TraceBundle(
            inferred_requirements=["Request screened by safety module."],
            plan=["Refuse unsafe request."],
            assumptions_and_confidence=["Confidence: 0.0"],
        )
        return None, trace, refusal

    inferred = [
        f"Goal interpreted as: {payload.problem_statement}",
        f"Industry context: {payload.industry}",
        f"Objective type: {payload.objective_type}",
    ]

    if payload.objective_type == "Analyze Data (CSV/Excel)" and payload.tabular_df is not None:
        routed = "Data Analyst Agent"
        result, trace_data = data_analyst.run(payload.problem_statement, payload.constraints, payload.tabular_df)
    elif payload.objective_type == "Decide Strategy (no data needed)":
        routed = "Multi-Agent Boardroom"
        result, trace_data = boardroom.run(payload.problem_statement, payload.constraints, payload.industry)
    elif payload.objective_type == "Design a Process (SOP/workflow)":
        routed = "Process Redesign Agent"
        result, trace_data = process_designer.run(payload.problem_statement, payload.constraints, bool(payload.sop_bytes))
    else:
        routed = "Ops Diagnostic Agent"
        result, trace_data = ops_diagnoser.run(payload.problem_statement, payload.constraints, payload.metrics_bytes)

    result["recommendations"]["actions"] = enforce_constraints(payload.constraints, result["recommendations"]["actions"])
    result["executive_summary"] = _rewrite_for_stakeholder(result["executive_summary"], payload.stakeholder_mode)
    result["confidence"] = _confidence_by_mode(payload.confidence_mode, result["confidence"])

    if payload.explain_mode:
        result["assumptions"].append("Explain mode enabled: intermediate steps surfaced for transparency.")

    output = AgentOutput(**result)

    trace = TraceBundle(
        inferred_requirements=inferred,
        plan=[
            "Interpret user objective and constraints.",
            f"Route to specialist: {routed}.",
            "Execute tools and compile evidence.",
            "Generate structured recommendations and 90-day plan.",
            "Render stakeholder-ready artifacts.",
        ],
        tool_calls=trace_data.get("tool_calls", []),
        evidence=trace_data.get("evidence", []),
        assumptions_and_confidence=[*output.assumptions, f"Confidence: {output.confidence:.2f}"],
        memory=[f"Stakeholder mode: {payload.stakeholder_mode}", f"Confidence mode: {payload.confidence_mode}"],
        routed_agent=routed,
    )
    return output, trace, None

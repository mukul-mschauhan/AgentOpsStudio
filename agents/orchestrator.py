from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from types import ModuleType
from typing import TYPE_CHECKING, List, Optional, Tuple

from schemas.output_schema import AgentOutput, TraceBundle
from tools.llm_gemini import generate_structured_output
from tools.safety import enforce_constraints, refusal_check

if TYPE_CHECKING:
    import pandas as pd


@dataclass
class OrchestratorInput:
    industry: str
    objective_type: str
    problem_statement: str
    constraints: List[str]
    explain_mode: bool
    stakeholder_mode: str
    confidence_mode: str
    tabular_df: Optional["pd.DataFrame"] = None
    sop_bytes: Optional[bytes] = None
    metrics_bytes: Optional[bytes] = None
    gemini_api_key: Optional[str] = None
    use_gemini: bool = False


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


def _load_specialists() -> tuple[ModuleType, ModuleType, ModuleType, ModuleType]:
    boardroom = import_module(".boardroom", package=__package__)
    data_analyst = import_module(".data_analyst", package=__package__)
    ops_diagnoser = import_module(".ops_diagnoser", package=__package__)
    process_designer = import_module(".process_designer", package=__package__)
    return boardroom, data_analyst, ops_diagnoser, process_designer


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

    try:
        boardroom, data_analyst, ops_diagnoser, process_designer = _load_specialists()
    except Exception as exc:  # noqa: BLE001
        trace = TraceBundle(
            inferred_requirements=inferred,
            plan=["Load specialist modules.", "Route to selected specialist."],
            assumptions_and_confidence=["Confidence: 0.0"],
        )
        return None, trace, f"Agent modules could not be loaded: {exc}"

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

    llm_error = None
    if payload.use_gemini and payload.gemini_api_key:
        try:
            result = generate_structured_output(
                api_key=payload.gemini_api_key,
                industry=payload.industry,
                objective_type=payload.objective_type,
                problem_statement=payload.problem_statement,
                constraints=payload.constraints,
                draft_result=result,
            )
            trace_data.setdefault("tool_calls", []).append(
                {"tool": "gemini_generate_structured_output", "input": {"model": "gemini-1.5-flash"}, "output": "LLM enhanced output"}
            )
        except Exception as exc:  # noqa: BLE001
            llm_error = str(exc)

    result["recommendations"]["actions"] = enforce_constraints(payload.constraints, result["recommendations"]["actions"])
    result["executive_summary"] = _rewrite_for_stakeholder(result["executive_summary"], payload.stakeholder_mode)
    result["confidence"] = _confidence_by_mode(payload.confidence_mode, result["confidence"])

    if payload.explain_mode:
        result["assumptions"].append("Explain mode enabled: intermediate steps surfaced for transparency.")
    if llm_error:
        result["assumptions"].append("Gemini fallback: deterministic logic was used because LLM call failed.")

    output = AgentOutput(**result)

    assumptions = [*output.assumptions, f"Confidence: {output.confidence:.2f}"]
    if llm_error:
        assumptions.append(f"Gemini error: {llm_error}")

    trace = TraceBundle(
        inferred_requirements=inferred,
        plan=[
            "Interpret user objective and constraints.",
            f"Route to specialist: {routed}.",
            "Execute tools and compile evidence.",
            "Optionally enhance output with Gemini.",
            "Render stakeholder-ready artifacts.",
        ],
        tool_calls=trace_data.get("tool_calls", []),
        evidence=trace_data.get("evidence", []),
        assumptions_and_confidence=assumptions,
        memory=[f"Stakeholder mode: {payload.stakeholder_mode}", f"Confidence mode: {payload.confidence_mode}"],
        routed_agent=routed,
    )
    return output, trace, None

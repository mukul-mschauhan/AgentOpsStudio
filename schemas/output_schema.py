from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


Severity = Literal["high", "med", "low"]


class ChartSpec(BaseModel):
    title: str
    type: str
    cols: List[str] = Field(default_factory=list)


class ActionItem(BaseModel):
    action: str
    owner: str
    timeframe: str
    impact: str


class RiskItem(BaseModel):
    risk: str
    severity: Severity
    mitigation: str


class ProblemUnderstanding(BaseModel):
    goal: str
    success_metrics: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)


class AnalysisSection(BaseModel):
    key_findings: List[str] = Field(default_factory=list)
    charts: List[ChartSpec] = Field(default_factory=list)
    anomalies: List[str] = Field(default_factory=list)


class RecommendationSection(BaseModel):
    actions: List[ActionItem] = Field(default_factory=list)
    risks: List[RiskItem] = Field(default_factory=list)
    plan_90_days: List[str] = Field(default_factory=list)


class AgentOutput(BaseModel):
    executive_summary: List[str] = Field(default_factory=list)
    problem_understanding: ProblemUnderstanding
    analysis: AnalysisSection
    recommendations: RecommendationSection
    assumptions: List[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)


class TraceBundle(BaseModel):
    inferred_requirements: List[str] = Field(default_factory=list)
    plan: List[str] = Field(default_factory=list)
    tool_calls: List[dict] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)
    assumptions_and_confidence: List[str] = Field(default_factory=list)
    memory: List[str] = Field(default_factory=list)
    routed_agent: Optional[str] = None

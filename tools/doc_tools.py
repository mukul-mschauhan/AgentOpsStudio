from __future__ import annotations

from typing import List

import pandas as pd


def build_cfo_memo(summary: List[str], risks: List[dict], actions: List[dict]) -> str:
    lines = [
        "# CFO Memo: AgentOps Studio Recommendation",
        "",
        "## Executive Snapshot",
    ]
    lines.extend([f"- {item}" for item in summary[:5]])
    lines.append("\n## Key Risks")
    for risk in risks[:5]:
        lines.append(f"- [{risk['severity'].upper()}] {risk['risk']} | Mitigation: {risk['mitigation']}")
    lines.append("\n## Priority Actions")
    for action in actions[:8]:
        lines.append(f"- {action['action']} (Owner: {action['owner']}, Timeframe: {action['timeframe']})")
    return "\n".join(lines)


def actions_to_csv(actions: List[dict]) -> str:
    df = pd.DataFrame(actions)
    if df.empty:
        df = pd.DataFrame([{"action": "No actions generated", "owner": "TBD", "timeframe": "TBD", "impact": "TBD"}])
    return df.to_csv(index=False)


def build_ops_action_plan(actions: List[dict], plan_90_days: List[str]) -> str:
    lines = ["# Ops Action Plan", "", "## Action Register"]
    for idx, action in enumerate(actions, start=1):
        lines.append(f"{idx}. {action['action']} | Owner: {action['owner']} | Impact: {action['impact']}")
    lines.append("\n## 90-Day Execution Cadence")
    lines.extend([f"- {item}" for item in plan_90_days])
    return "\n".join(lines)

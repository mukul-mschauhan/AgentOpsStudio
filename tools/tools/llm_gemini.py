from __future__ import annotations

import json
import re
from typing import Any, Dict, List

import requests

from schemas.output_schema import AgentOutput

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"


def _extract_json_block(text: str) -> Dict[str, Any]:
    fenced = re.search(r"```json\s*(\{.*?\})\s*```", text, flags=re.DOTALL)
    if fenced:
        return json.loads(fenced.group(1))
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return json.loads(text[start : end + 1])
    raise ValueError("Model response did not contain JSON.")


def _build_prompt(problem: str, industry: str, objective_type: str, constraints: List[str], draft: Dict[str, Any]) -> str:
    return (
        "You are an enterprise strategy and operations AI assistant. "
        "Return ONLY valid JSON that matches this exact schema keys: "
        "executive_summary (list of 5 short bullets), problem_understanding{goal,success_metrics,constraints}, "
        "analysis{key_findings,charts,anomalies}, recommendations{actions,risks,plan_90_days}, assumptions, confidence. "
        "Do not include markdown or commentary.\n\n"
        f"Industry: {industry}\n"
        f"Objective Type: {objective_type}\n"
        f"Problem: {problem}\n"
        f"Constraints: {constraints}\n\n"
        "Use this baseline analysis and improve it while keeping claims realistic:\n"
        f"{json.dumps(draft)}"
    )


def generate_structured_output(
    *,
    api_key: str,
    industry: str,
    objective_type: str,
    problem_statement: str,
    constraints: List[str],
    draft_result: Dict[str, Any],
) -> Dict[str, Any]:
    if not api_key:
        raise ValueError("Missing Gemini API key.")

    body = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": _build_prompt(
                            problem_statement,
                            industry,
                            objective_type,
                            constraints,
                            draft_result,
                        )
                    }
                ],
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "response_mime_type": "application/json",
        },
    }

    response = requests.post(
        f"{GEMINI_URL}?key={api_key}",
        headers={"Content-Type": "application/json"},
        json=body,
        timeout=40,
    )
    response.raise_for_status()
    data = response.json()
    text = data["candidates"][0]["content"]["parts"][0]["text"]
    parsed = _extract_json_block(text)
    validated = AgentOutput(**parsed)
    return validated.model_dump()

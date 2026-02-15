# AgentOps Studio

AgentOps Studio is a Streamlit demo app that showcases an **AI agent as a visible worker**:

- What the user asked
- What the agent inferred
- What plan it created
- What tools it ran
- What outputs it produced
- Confidence + assumptions
- Next actions

## Features

- 3-panel UI: Inputs / Outputs / Agent Trace
- Routing orchestrator with specialist agents:
  - Data Analyst Agent
  - Multi-Agent Boardroom
  - Process Redesign Agent
  - Ops Diagnostic Agent
- Structured output schema for predictable delivery
- Downloadable deliverables:
  - CFO memo
  - Ops action plan
  - JIRA-ready CSV tasks
- Lightweight memory persisted to `memory/session_memory.json`

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Demo flow for workshops

1. Choose an industry + objective type.
2. Enter a business problem and constraints.
3. Optionally upload CSV/SOP/metrics JSON.
4. Click **Run Agent**.
5. Walk stakeholders through the right-side trace.

## Repo structure

```text
agentops-studio/
  app.py
  requirements.txt
  README.md
  assets/
  agents/
  tools/
  schemas/
  memory/
  samples/
```


## Streamlit Cloud troubleshooting

If your deployed app still shows old errors after a fix:

1. Confirm the deploy points to the latest commit on the `main` branch.
2. In Streamlit Cloud, click **Relaunch app** (or reboot from app settings).
3. If needed, clear app cache and rerun.

This project no longer uses `use_container_width` and should not raise that warning on current code.

## Notes

- This starter uses deterministic, heuristic logic so it works out-of-the-box.
- You can later integrate Gemini/OpenAI/Azure in specialist agents.

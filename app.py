from __future__ import annotations

from typing import List

import streamlit as st

from agents.orchestrator import OrchestratorInput, run_agent
from memory.store import load_memory, update_memory
from tools.data_tools import load_tabular_file
from tools.doc_tools import actions_to_csv, build_cfo_memo, build_ops_action_plan
from tools.viz_tools import render_chart

st.set_page_config(page_title="AgentOps Studio", layout="wide")

st.title("🤖 AgentOps Studio")
st.caption("Pick an industry → describe the problem → upload data (optional) → the agent plans, executes, and delivers stakeholder-ready outcomes.")

memory = load_memory()

for key, default in {
    "last_output": None,
    "last_trace": None,
    "last_refusal": None,
    "last_problem": "",
    "last_df": None,
    "last_error": None,
}.items():
    st.session_state.setdefault(key, default)

with st.sidebar:
    st.header("Inputs")
    industry = st.selectbox("Industry", ["Manufacturing", "Healthcare", "Finance", "IT Ops", "Other"])
    objective_type = st.radio(
        "Objective Type",
        [
            "Analyze Data (CSV/Excel)",
            "Decide Strategy (no data needed)",
            "Design a Process (SOP/workflow)",
            "Monitor & Diagnose (metrics/logs)",
        ],
    )
    problem_statement = st.text_area("Problem Statement", placeholder="Write your business problem in plain English…")

    st.subheader("Constraints")
    quick_constraints = st.multiselect(
        "Select constraints",
        ["Time limit", "Budget limit", "Compliance: HIPAA", "Compliance: PCI", "Compliance: GDPR", "Cloud", "On-prem", "Edge", "Latency <200ms"],
    )
    extra_constraints = st.text_input("Other constraints")

    st.subheader("Innovative Controls")
    explain_mode = st.toggle("Explain Like I'm New", value=True)
    stakeholder_mode = st.selectbox("Stakeholder Mode", ["CFO", "Plant Manager", "CISO", "Product Head"], index=0)
    confidence_mode = st.select_slider("Confidence Slider", options=["Conservative", "Balanced", "Aggressive"], value="Balanced")

    st.subheader("Attachments")
    tabular_file = st.file_uploader("Upload CSV/Excel", type=["csv", "xlsx", "xls"])
    sop_file = st.file_uploader("Upload PDF/SOP (optional)", type=["pdf", "txt", "docx"])
    metrics_file = st.file_uploader("Upload metrics JSON (optional)", type=["json"])

    col_a, col_b = st.columns(2)
    run_clicked = col_a.button("Run Agent", type="primary")
    explain_clicked = col_b.button("Run with Explain Mode")

constraints: List[str] = quick_constraints + ([extra_constraints] if extra_constraints else [])
if explain_clicked:
    explain_mode = True

should_run = run_clicked or explain_clicked
if should_run:
    try:
        st.session_state.last_error = None
        if not problem_statement.strip():
            st.warning("Please enter a problem statement before running the agent.")
        else:
            df = None
            if tabular_file is not None:
                df = load_tabular_file(tabular_file.getvalue(), tabular_file.name)

            if objective_type == "Analyze Data (CSV/Excel)" and df is None:
                st.warning("For **Analyze Data**, please upload a CSV or Excel file.")
            else:
                payload = OrchestratorInput(
                    industry=industry,
                    objective_type=objective_type,
                    problem_statement=problem_statement,
                    constraints=constraints,
                    explain_mode=explain_mode,
                    stakeholder_mode=stakeholder_mode,
                    confidence_mode=confidence_mode,
                    tabular_df=df,
                    sop_bytes=sop_file.getvalue() if sop_file else None,
                    metrics_bytes=metrics_file.getvalue() if metrics_file else None,
                )

                with st.spinner("Running agent workflow..."):
                    output, trace, refusal = run_agent(payload)

                st.session_state.last_output = output
                st.session_state.last_trace = trace
                st.session_state.last_refusal = refusal
                st.session_state.last_problem = problem_statement
                st.session_state.last_df = df

                update_memory(
                    {
                        "industry": industry,
                        "objective_type": objective_type,
                        "stakeholder_mode": stakeholder_mode,
                        "confidence_mode": confidence_mode,
                        "constraints": constraints,
                    }
                )
    except Exception as exc:  # noqa: BLE001
        st.session_state.last_error = str(exc)

output = st.session_state.last_output
trace = st.session_state.last_trace
refusal = st.session_state.last_refusal
problem_to_show = st.session_state.last_problem
df = st.session_state.last_df

if st.session_state.last_error:
    st.error(f"Agent run failed: {st.session_state.last_error}")
    st.info("Tip: No API key is needed for this starter build. Check logs for parsing/file issues.")

if output is not None and trace is not None:
    left, center, right = st.columns([1, 2, 1])

    with left:
        st.markdown("### User Ask")
        st.write(problem_to_show or "(No problem entered)")
        st.markdown("### Agent Inference")
        for item in trace.inferred_requirements:
            st.markdown(f"- {item}")

    with center:
        if refusal:
            st.error(refusal)
        else:
            tabs = st.tabs(["Executive Answer", "Deliverables", "Interactive Q&A"])

            with tabs[0]:
                st.subheader("Summary")
                for bullet in output.executive_summary:
                    st.markdown(f"- {bullet}")
                st.subheader("Top Risks")
                st.table([r.model_dump() for r in output.recommendations.risks])
                st.subheader("Recommended Actions")
                st.dataframe([a.model_dump() for a in output.recommendations.actions], width="stretch")
                st.subheader("90-Day Plan")
                for line in output.recommendations.plan_90_days:
                    st.markdown(f"- {line}")
                st.metric("Confidence", f"{output.confidence:.0%}")

                if df is not None and output.analysis.charts:
                    st.subheader("Charts")
                    for spec in output.analysis.charts:
                        fig = render_chart(df, spec.model_dump())
                        if fig:
                            st.plotly_chart(fig, width="stretch")

            with tabs[1]:
                memo = build_cfo_memo(output.executive_summary, [r.model_dump() for r in output.recommendations.risks], [a.model_dump() for a in output.recommendations.actions])
                action_plan = build_ops_action_plan([a.model_dump() for a in output.recommendations.actions], output.recommendations.plan_90_days)
                jira_csv = actions_to_csv([a.model_dump() for a in output.recommendations.actions])

                st.download_button("Download CFO Memo (.md)", memo, file_name="cfo_memo.md")
                st.download_button("Download Ops Action Plan (.md)", action_plan, file_name="ops_action_plan.md")
                st.download_button("Download JIRA Tasks (.csv)", jira_csv, file_name="jira_tasks.csv")
                st.json(output.model_dump())

            with tabs[2]:
                st.info("Ask follow-up questions in your workshop and rerun with changed assumptions (e.g., budget cut by 40%).")
                follow_up = st.text_input("Ask a what-if question")
                if follow_up:
                    st.write("Suggested response strategy:")
                    st.markdown(f"- Re-plan against: **{follow_up}**")
                    st.markdown("- Reuse existing evidence and update assumptions/confidence.")

    with right:
        st.markdown("### Agent Trace")
        with st.expander("Inferred Requirements", expanded=True):
            st.write(trace.inferred_requirements)
        with st.expander("Plan", expanded=True):
            st.write(trace.plan)
        with st.expander("Tool Calls", expanded=False):
            st.json(trace.tool_calls)
        with st.expander("Evidence", expanded=False):
            st.write(trace.evidence)
        with st.expander("Assumptions & Confidence", expanded=True):
            st.write(trace.assumptions_and_confidence)
        with st.expander("Memory", expanded=False):
            st.write({**memory, "session": trace.memory})

else:
    st.info("Configure inputs in the left sidebar and click **Run Agent**.")
    st.caption("You do not need an API key for this deterministic demo version.")

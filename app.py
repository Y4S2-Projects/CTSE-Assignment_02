import html
import os
import sys
import time

import streamlit as st

# Ensure the core and agents packages can be imported
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from core.state import state
from pipeline import run_system


AGENT_STEPS = [
    {
        "key": "question",
        "name": "Coordinator",
        "role": "Plans the assignment",
        "result": "plan",
        "accent": "#2563eb",
    },
    {
        "key": "plan",
        "name": "Researcher",
        "role": "Collects useful context",
        "result": "research",
        "accent": "#0f766e",
    },
    {
        "key": "research",
        "name": "Writer",
        "role": "Builds the full draft",
        "result": "draft",
        "accent": "#b45309",
    },
    {
        "key": "draft",
        "name": "Evaluator",
        "role": "Checks quality and structure",
        "result": "evaluation",
        "accent": "#7c3aed",
    },
]


def inject_styles() -> None:
    st.markdown(
        """
        <style>
            :root {
                --ink: #0f172a;
                --muted: #64748b;
                --line: #dbe3ee;
                --panel: #ffffff;
                --soft: #f8fafc;
                --blue: #2563eb;
                --teal: #0f766e;
                --amber: #b45309;
                --violet: #7c3aed;
                --green: #15803d;
                --red: #b91c1c;
            }

            .stApp {
                background:
                    radial-gradient(circle at top left, rgba(37, 99, 235, 0.12), transparent 32rem),
                    linear-gradient(135deg, #f8fafc 0%, #eef6f4 42%, #f7f3ff 100%);
                color: var(--ink);
            }

            .block-container {
                padding-top: 2rem;
                padding-bottom: 2rem;
                max-width: 1240px;
            }

            [data-testid="stSidebar"] {
                background: #0f172a;
            }

            [data-testid="stSidebar"] * {
                color: #e5eefb !important;
            }

            [data-testid="stSidebar"] .stSelectbox label,
            [data-testid="stSidebar"] .stToggle label {
                color: #f8fafc !important;
            }

            .hero-shell {
                border: 1px solid rgba(15, 23, 42, 0.08);
                background: rgba(255, 255, 255, 0.82);
                backdrop-filter: blur(18px);
                border-radius: 20px;
                padding: 28px;
                box-shadow: 0 24px 70px rgba(15, 23, 42, 0.10);
            }

            .hero-grid {
                display: grid;
                grid-template-columns: minmax(0, 1.2fr) minmax(280px, 0.8fr);
                gap: 22px;
                align-items: stretch;
            }

            .eyebrow {
                color: var(--blue);
                font-size: 0.78rem;
                font-weight: 800;
                letter-spacing: 0;
                margin-bottom: 10px;
                text-transform: uppercase;
            }

            .hero-title {
                color: var(--ink);
                font-size: clamp(2rem, 4vw, 4.1rem);
                font-weight: 850;
                letter-spacing: 0;
                line-height: 1.02;
                margin: 0;
            }

            .hero-copy {
                color: var(--muted);
                font-size: 1.02rem;
                line-height: 1.7;
                margin: 18px 0 0;
                max-width: 720px;
            }

            .metric-row {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 10px;
                margin-top: 24px;
            }

            .metric {
                background: var(--soft);
                border: 1px solid var(--line);
                border-radius: 14px;
                padding: 14px;
            }

            .metric strong {
                display: block;
                color: var(--ink);
                font-size: 1.3rem;
                line-height: 1;
            }

            .metric span {
                color: var(--muted);
                display: block;
                font-size: 0.78rem;
                margin-top: 7px;
            }

            .flow-panel {
                background: #0f172a;
                border-radius: 18px;
                min-height: 100%;
                overflow: hidden;
                padding: 18px;
                position: relative;
            }

            .flow-panel:before {
                background: linear-gradient(90deg, #22c55e, #38bdf8, #a78bfa, #f59e0b);
                content: "";
                height: 4px;
                left: 0;
                position: absolute;
                right: 0;
                top: 0;
            }

            .flow-panel h3 {
                color: #f8fafc;
                font-size: 1rem;
                letter-spacing: 0;
                margin: 0 0 16px;
            }

            .mini-flow-step {
                align-items: center;
                display: grid;
                grid-template-columns: 38px minmax(0, 1fr);
                gap: 12px;
                padding: 10px 0;
                position: relative;
            }

            .mini-flow-step + .mini-flow-step {
                border-top: 1px solid rgba(226, 232, 240, 0.12);
            }

            .mini-dot {
                align-items: center;
                background: rgba(255,255,255,0.10);
                border: 1px solid rgba(255,255,255,0.18);
                border-radius: 999px;
                color: #f8fafc;
                display: flex;
                font-weight: 800;
                height: 38px;
                justify-content: center;
                width: 38px;
            }

            .mini-flow-step strong {
                color: #f8fafc;
                display: block;
                font-size: 0.92rem;
            }

            .mini-flow-step span {
                color: #b6c5d8;
                display: block;
                font-size: 0.78rem;
                line-height: 1.35;
                margin-top: 3px;
            }

            .section-label {
                color: var(--ink);
                font-size: 1.15rem;
                font-weight: 800;
                letter-spacing: 0;
                margin: 1.2rem 0 0.8rem;
            }

            .agent-flow {
                display: grid;
                gap: 12px;
                grid-template-columns: repeat(4, minmax(0, 1fr));
            }

            .agent-card {
                background: rgba(255,255,255,0.90);
                border: 1px solid var(--line);
                border-radius: 16px;
                box-shadow: 0 18px 40px rgba(15, 23, 42, 0.07);
                min-height: 150px;
                overflow: hidden;
                padding: 16px;
                position: relative;
            }

            .agent-card:before {
                background: var(--accent);
                content: "";
                height: 5px;
                left: 0;
                position: absolute;
                right: 0;
                top: 0;
            }

            .agent-head {
                align-items: center;
                display: flex;
                gap: 10px;
            }

            .agent-index {
                align-items: center;
                background: color-mix(in srgb, var(--accent) 14%, white);
                border: 1px solid color-mix(in srgb, var(--accent) 28%, white);
                border-radius: 12px;
                color: var(--accent);
                display: flex;
                font-weight: 850;
                height: 36px;
                justify-content: center;
                width: 36px;
            }

            .agent-card h4 {
                color: var(--ink);
                font-size: 0.98rem;
                letter-spacing: 0;
                margin: 0;
            }

            .agent-card p {
                color: var(--muted);
                font-size: 0.82rem;
                line-height: 1.45;
                margin: 7px 0 0;
            }

            .status-pill {
                border-radius: 999px;
                display: inline-flex;
                font-size: 0.72rem;
                font-weight: 800;
                margin-top: 16px;
                padding: 6px 10px;
            }

            .status-ready {
                background: #eef2ff;
                color: #3730a3;
            }

            .status-running {
                background: #fff7ed;
                color: #9a3412;
            }

            .status-done {
                background: #ecfdf5;
                color: #047857;
            }

            .output-flow {
                display: grid;
                gap: 12px;
                grid-template-columns: repeat(6, minmax(0, 1fr));
            }

            .output-node {
                background: rgba(255,255,255,0.92);
                border: 1px solid var(--line);
                border-radius: 14px;
                min-height: 142px;
                padding: 14px;
            }

            .output-node strong {
                color: var(--ink);
                display: block;
                font-size: 0.88rem;
            }

            .output-node span {
                color: var(--muted);
                display: block;
                font-size: 0.76rem;
                line-height: 1.45;
                margin-top: 8px;
                overflow-wrap: anywhere;
            }

            .success-banner {
                align-items: center;
                background: #ecfdf5;
                border: 1px solid #bbf7d0;
                border-radius: 16px;
                color: #065f46;
                display: flex;
                font-weight: 800;
                justify-content: space-between;
                margin: 1rem 0;
                padding: 14px 16px;
            }

            .success-banner span {
                color: #047857;
                font-size: 0.86rem;
                font-weight: 700;
            }

            .stButton > button {
                border-radius: 12px;
                font-weight: 800;
                min-height: 3rem;
            }

            textarea {
                border-radius: 14px !important;
            }

            @media (max-width: 980px) {
                .hero-grid,
                .agent-flow,
                .output-flow,
                .metric-row {
                    grid-template-columns: 1fr;
                }

                .hero-shell {
                    padding: 20px;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def safe_preview(value, limit: int = 140) -> str:
    if value is None:
        return "Waiting for this step to complete."
    if isinstance(value, dict):
        value = " | ".join(f"{key}: {item}" for key, item in value.items())
    text = " ".join(str(value).split())
    if len(text) > limit:
        text = f"{text[:limit].rstrip()}..."
    return html.escape(text)


def render_hero() -> None:
    steps_html = "".join(
        f"""
        <div class="mini-flow-step">
            <div class="mini-dot">{index}</div>
            <div>
                <strong>{step["name"]}</strong>
                <span>{step["role"]}</span>
            </div>
        </div>
        """
        for index, step in enumerate(AGENT_STEPS, start=1)
    )

    st.markdown(
        f"""
        <div class="hero-shell">
            <div class="hero-grid">
                <div>
                    <div class="eyebrow">Local multi-agent assignment studio</div>
                    <h1 class="hero-title">Generate structured answers with a visible agent workflow.</h1>
                    <p class="hero-copy">
                        Enter an assignment topic and watch the system move from planning to research,
                        drafting, evaluation, and final output in one clean workspace.
                    </p>
                    <div class="metric-row">
                        <div class="metric"><strong>4</strong><span>Specialized agents</span></div>
                        <div class="metric"><strong>2x</strong><span>Draft refinement loop</span></div>
                        <div class="metric"><strong>Local</strong><span>Ollama-powered run</span></div>
                    </div>
                </div>
                <div class="flow-panel">
                    <h3>Agent route</h3>
                    {steps_html}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_agent_flow(mode: str = "ready") -> None:
    labels = {
        "ready": ("Ready", "status-ready"),
        "running": ("Working", "status-running"),
        "done": ("Completed", "status-done"),
    }
    label, class_name = labels.get(mode, labels["ready"])

    cards = "".join(
        f"""
        <div class="agent-card" style="--accent:{step["accent"]};">
            <div class="agent-head">
                <div class="agent-index">{index}</div>
                <div>
                    <h4>{step["name"]}</h4>
                    <p>{step["role"]}</p>
                </div>
            </div>
            <span class="status-pill {class_name}">{label}</span>
        </div>
        """
        for index, step in enumerate(AGENT_STEPS, start=1)
    )

    st.markdown(
        f"""
        <div class="section-label">Agent Flow</div>
        <div class="agent-flow">{cards}</div>
        """,
        unsafe_allow_html=True,
    )


def render_output_flow(full_state: dict, final_answer: str) -> None:
    nodes = [
        ("Question", full_state.get("question")),
        ("Plan", full_state.get("plan")),
        ("Research", full_state.get("research")),
        ("Draft", full_state.get("draft")),
        ("Evaluation", full_state.get("evaluation")),
        ("Final Output", final_answer),
    ]

    node_html = "".join(
        f"""
        <div class="output-node">
            <strong>{html.escape(title)}</strong>
            <span>{safe_preview(value)}</span>
        </div>
        """
        for title, value in nodes
    )

    st.markdown(
        f"""
        <div class="section-label">Final Output Flow</div>
        <div class="output-flow">{node_html}</div>
        """,
        unsafe_allow_html=True,
    )


st.set_page_config(
    page_title="Smart Assignment Helper",
    page_icon="AI",
    layout="wide",
)

inject_styles()

with st.sidebar:
    st.markdown("## Settings")
    selected_model = st.selectbox("Model selection", ["llama3", "phi3"], index=0)
    show_logs = st.toggle("Show debug state", value=False)
    st.markdown("---")
    st.info(
        "The interface shows the full multi-agent route while the existing backend runs the local Ollama pipeline."
    )
    st.caption(f"Selected UI model preference: {selected_model}")

render_hero()
render_agent_flow("ready")

st.markdown('<div class="section-label">Assignment Input</div>', unsafe_allow_html=True)
question = st.text_area(
    "Assignment topic",
    height=155,
    label_visibility="collapsed",
    placeholder="Example: Explain the role of DevOps in current trends in software engineering.",
)

generate_btn = st.button("Generate assignment answer", type="primary", use_container_width=True)

if generate_btn:
    if not question.strip():
        st.warning("Please enter an assignment question to generate an answer.")
    else:
        state.state = {
            "question": None,
            "plan": None,
            "research": None,
            "draft": None,
            "evaluation": None,
        }

        start_time = time.time()
        progress_placeholder = st.empty()

        with progress_placeholder.container():
            render_agent_flow("running")

        with st.spinner("Agents are planning, researching, writing, and evaluating..."):
            try:
                final_answer, evaluation, full_state = run_system(question)
                execution_time = time.time() - start_time

                with progress_placeholder.container():
                    render_agent_flow("done")

                status = evaluation.get("status", "Unknown") if isinstance(evaluation, dict) else "Unknown"
                feedback = (
                    evaluation.get("feedback", "No feedback provided.")
                    if isinstance(evaluation, dict)
                    else "No feedback provided."
                )

                st.markdown(
                    f"""
                    <div class="success-banner">
                        <div>Assignment generated successfully</div>
                        <span>{execution_time:.2f} seconds | Evaluation: {html.escape(status)}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                render_output_flow(full_state, final_answer)

                tabs = st.tabs(
                    [
                        "Final Answer",
                        "Evaluation",
                        "Agent State",
                    ]
                )

                with tabs[0]:
                    st.markdown("### Generated Assignment")
                    st.markdown(final_answer)

                with tabs[1]:
                    col_status, col_feedback = st.columns([1, 3])
                    with col_status:
                        if status == "Good":
                            st.success(f"Status: {status}")
                        else:
                            st.warning(f"Status: {status}")

                    with col_feedback:
                        st.markdown("#### Evaluator Feedback")
                        st.write(feedback)

                with tabs[2]:
                    if show_logs:
                        st.json(full_state)
                    else:
                        st.info("Turn on 'Show debug state' in the sidebar to inspect the internal agent state.")

            except Exception as exc:
                progress_placeholder.empty()
                render_agent_flow("ready")
                st.error(f"An error occurred during system execution: {exc}")

st.divider()
st.caption("Smart Assignment Helper | Multi-Agent AI | SLIIT CTSE Assignment | Ollama Local AI")

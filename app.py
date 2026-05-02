import html
import os
import re
import sys
import textwrap
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


def inject_styles(theme_mode: str = "Light") -> None:
    if theme_mode == "Dark":
        palette = {
            "app_bg": "linear-gradient(135deg, #08111f 0%, #101827 46%, #171225 100%)",
            "ink": "#f8fafc",
            "muted": "#cbd5e1",
            "line": "#334155",
            "panel": "#111827",
            "panel_soft": "#172033",
            "soft": "#1f2937",
            "input": "#0f172a",
            "shadow": "0 24px 70px rgba(0, 0, 0, 0.32)",
            "sidebar": "#050b14",
            "success_bg": "#052e1a",
            "success_line": "#166534",
            "success_text": "#dcfce7",
            "success_muted": "#86efac",
            "button_bg": "#38bdf8",
            "button_text": "#07111f",
            "button_hover": "#7dd3fc",
        }
    else:
        palette = {
            "app_bg": "linear-gradient(135deg, #f8fafc 0%, #eef6f4 42%, #f7f3ff 100%)",
            "ink": "#0f172a",
            "muted": "#64748b",
            "line": "#dbe3ee",
            "panel": "#ffffff",
            "panel_soft": "#f8fafc",
            "soft": "#f8fafc",
            "input": "#ffffff",
            "shadow": "0 24px 70px rgba(15, 23, 42, 0.10)",
            "sidebar": "#0f172a",
            "success_bg": "#ecfdf5",
            "success_line": "#bbf7d0",
            "success_text": "#065f46",
            "success_muted": "#047857",
            "button_bg": "#2563eb",
            "button_text": "#ffffff",
            "button_hover": "#1d4ed8",
        }

    css = """
        <style>
            :root {
                --ink: __INK__;
                --muted: __MUTED__;
                --line: __LINE__;
                --panel: __PANEL__;
                --panel-soft: __PANEL_SOFT__;
                --soft: __SOFT__;
                --input: __INPUT__;
                --app-bg: __APP_BG__;
                --shadow: __SHADOW__;
                --sidebar-bg: __SIDEBAR__;
                --success-bg: __SUCCESS_BG__;
                --success-line: __SUCCESS_LINE__;
                --success-text: __SUCCESS_TEXT__;
                --success-muted: __SUCCESS_MUTED__;
                --button-bg: __BUTTON_BG__;
                --button-text: __BUTTON_TEXT__;
                --button-hover: __BUTTON_HOVER__;
                --blue: #2563eb;
                --teal: #0f766e;
                --amber: #b45309;
                --violet: #7c3aed;
                --green: #15803d;
                --red: #b91c1c;
            }

            .stApp {
                background: var(--app-bg);
                color: var(--ink);
            }

            .stApp,
            .stApp p,
            .stApp span,
            .stApp label,
            .stApp div,
            .stApp h1,
            .stApp h2,
            .stApp h3,
            .stApp h4,
            .stApp h5,
            .stApp h6 {
                color: var(--ink);
            }

            .block-container {
                padding-top: 2rem;
                padding-bottom: 2rem;
                max-width: 1240px;
            }

            [data-testid="stSidebar"] {
                background: var(--sidebar-bg);
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
                background: color-mix(in srgb, var(--panel) 88%, transparent);
                backdrop-filter: blur(18px);
                border-radius: 20px;
                padding: 28px;
                box-shadow: var(--shadow);
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
                background: var(--panel-soft);
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
                background: var(--panel);
                border: 1px solid var(--line);
                border-radius: 16px;
                box-shadow: var(--shadow);
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
                background: var(--panel);
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
                background: var(--success-bg);
                border: 1px solid var(--success-line);
                border-radius: 16px;
                color: var(--success-text);
                display: flex;
                font-weight: 800;
                justify-content: space-between;
                margin: 1rem 0;
                padding: 14px 16px;
            }

            .success-banner div {
                color: var(--success-text);
            }

            .success-banner span {
                color: var(--success-muted);
                font-size: 0.86rem;
                font-weight: 700;
            }

            .stButton > button {
                background: var(--button-bg);
                border: 1px solid var(--button-bg);
                border-radius: 12px;
                color: var(--button-text);
                font-weight: 800;
                min-height: 3rem;
            }

            .stButton > button:hover {
                background: var(--button-hover);
                border-color: var(--button-hover);
                color: var(--button-text);
            }

            .stDownloadButton > button {
                background: var(--button-bg);
                border: 1px solid var(--button-bg);
                border-radius: 12px;
                color: var(--button-text) !important;
                font-weight: 850;
                min-height: 3rem;
            }

            .stDownloadButton > button:hover,
            .stDownloadButton > button:focus,
            .stDownloadButton > button:active {
                background: var(--button-hover);
                border-color: var(--button-hover);
                color: var(--button-text) !important;
            }

            .stDownloadButton > button * {
                color: var(--button-text) !important;
            }

            textarea,
            [data-baseweb="textarea"] textarea,
            [data-baseweb="input"] input {
                background: var(--input) !important;
                border-color: var(--line) !important;
                color: var(--ink) !important;
                border-radius: 14px !important;
            }

            textarea::placeholder,
            [data-baseweb="textarea"] textarea::placeholder {
                color: var(--muted) !important;
            }

            [data-testid="stMetric"] {
                background: var(--panel);
                border: 1px solid var(--line);
                border-radius: 14px;
                padding: 14px;
            }

            [data-testid="stMetric"] label,
            [data-testid="stMetric"] div,
            [data-testid="stMetric"] [data-testid="stMetricValue"] {
                color: var(--ink) !important;
            }

            [data-testid="stMetric"] label {
                color: var(--muted) !important;
            }

            [data-testid="stExpander"] {
                background: var(--panel);
                border: 1px solid var(--line);
                border-radius: 14px;
                overflow: hidden;
            }

            [data-testid="stExpander"] details,
            [data-testid="stExpander"] summary,
            [data-testid="stExpander"] p,
            [data-testid="stExpander"] div {
                color: var(--ink) !important;
            }

            [data-baseweb="tab-list"] {
                gap: 8px;
            }

            [data-baseweb="tab"] {
                background: var(--panel-soft);
                border: 1px solid var(--line);
                border-radius: 10px;
                color: var(--ink);
            }

            [data-baseweb="tab"] p,
            [data-baseweb="tab"] span {
                color: var(--ink) !important;
            }

            .download-report-panel {
                background: var(--panel);
                border: 1px solid var(--line);
                border-radius: 16px;
                box-shadow: var(--shadow);
                margin: 1rem 0;
                padding: 16px;
            }

            .download-report-panel,
            .download-report-panel * {
                color: var(--ink);
            }

            .download-report-panel p {
                color: var(--muted);
                margin: 0 0 12px;
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
        """
    replacements = {
        "__INK__": palette["ink"],
        "__MUTED__": palette["muted"],
        "__LINE__": palette["line"],
        "__PANEL__": palette["panel"],
        "__PANEL_SOFT__": palette["panel_soft"],
        "__SOFT__": palette["soft"],
        "__INPUT__": palette["input"],
        "__APP_BG__": palette["app_bg"],
        "__SHADOW__": palette["shadow"],
        "__SIDEBAR__": palette["sidebar"],
        "__SUCCESS_BG__": palette["success_bg"],
        "__SUCCESS_LINE__": palette["success_line"],
        "__SUCCESS_TEXT__": palette["success_text"],
        "__SUCCESS_MUTED__": palette["success_muted"],
        "__BUTTON_BG__": palette["button_bg"],
        "__BUTTON_TEXT__": palette["button_text"],
        "__BUTTON_HOVER__": palette["button_hover"],
    }
    for token, value in replacements.items():
        css = css.replace(token, value)

    st.markdown(
        css,
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
        (
            '<div class="mini-flow-step">'
            f'<div class="mini-dot">{index}</div>'
            "<div>"
            f'<strong>{html.escape(step["name"])}</strong>'
            f'<span>{html.escape(step["role"])}</span>'
            "</div>"
            "</div>"
        )
        for index, step in enumerate(AGENT_STEPS, start=1)
    )

    st.markdown(
        (
            '<div class="hero-shell">'
            '<div class="hero-grid">'
            "<div>"
            '<div class="eyebrow">Local multi-agent assignment studio</div>'
            '<h1 class="hero-title">Generate structured answers with a visible agent workflow.</h1>'
            '<p class="hero-copy">'
            "Enter an assignment topic and watch the system move from planning to research, "
            "drafting, evaluation, and final output in one clean workspace."
            "</p>"
            '<div class="metric-row">'
            '<div class="metric"><strong>4</strong><span>Specialized agents</span></div>'
            '<div class="metric"><strong>2x</strong><span>Draft refinement loop</span></div>'
            '<div class="metric"><strong>Local</strong><span>Ollama-powered run</span></div>'
            "</div>"
            "</div>"
            '<div class="flow-panel">'
            "<h3>Agent route</h3>"
            f"{steps_html}"
            "</div>"
            "</div>"
            "</div>"
        ),
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
        (
            f'<div class="agent-card" style="--accent:{step["accent"]};">'
            '<div class="agent-head">'
            f'<div class="agent-index">{index}</div>'
            "<div>"
            f'<h4>{html.escape(step["name"])}</h4>'
            f'<p>{html.escape(step["role"])}</p>'
            "</div>"
            "</div>"
            f'<span class="status-pill {class_name}">{label}</span>'
            "</div>"
        )
        for index, step in enumerate(AGENT_STEPS, start=1)
    )

    st.markdown(
        f'<div class="section-label">Agent Flow</div><div class="agent-flow">{cards}</div>',
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
        (
            '<div class="output-node">'
            f"<strong>{html.escape(title)}</strong>"
            f"<span>{safe_preview(value)}</span>"
            "</div>"
        )
        for title, value in nodes
    )

    st.markdown(
        (
            '<div class="section-label">Final Output Flow</div>'
            f'<div class="output-flow">{node_html}</div>'
        ),
        unsafe_allow_html=True,
    )


def split_assignment_sections(answer: str) -> list[tuple[str, str]]:
    sections = []
    current_title = "Overview"
    current_lines = []

    for line in (answer or "").splitlines():
        stripped = line.strip()
        heading_match = re.match(r"^(#{1,3}\s*)?(Introduction|Explanation|Examples|Advantages / Use cases|Conclusion)\s*$", stripped, re.I)
        if heading_match:
            if current_lines:
                sections.append((current_title, "\n".join(current_lines).strip()))
            current_title = heading_match.group(2)
            current_lines = []
        elif stripped.startswith("# "):
            if current_lines:
                sections.append((current_title, "\n".join(current_lines).strip()))
            current_title = stripped[2:].strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_lines:
        sections.append((current_title, "\n".join(current_lines).strip()))

    return [(title, body) for title, body in sections if body]


def _escape_pdf_text(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def create_assignment_pdf(title: str, answer: str, evaluation: dict) -> bytes:
    clean_title = " ".join((title or "Generated Assignment").split())
    clean_answer = re.sub(r"^#{1,6}\s*", "", answer or "", flags=re.MULTILINE)
    status = evaluation.get("status", "Unknown") if isinstance(evaluation, dict) else "Unknown"
    score = evaluation.get("score", "N/A") if isinstance(evaluation, dict) else "N/A"
    word_count = evaluation.get("word_count", len(clean_answer.split())) if isinstance(evaluation, dict) else len(clean_answer.split())

    lines = [
        clean_title,
        "",
        f"Evaluation Status: {status}",
        f"Score: {score}",
        f"Word Count: {word_count}",
        "",
    ]
    lines.extend(clean_answer.splitlines())

    wrapped_lines = []
    for line in lines:
        if not line.strip():
            wrapped_lines.append("")
            continue
        wrapped_lines.extend(textwrap.wrap(line, width=88) or [""])

    lines_per_page = 44
    pages = [
        wrapped_lines[index:index + lines_per_page]
        for index in range(0, len(wrapped_lines), lines_per_page)
    ] or [["Generated Assignment"]]

    objects = []
    pages_object_number = 2
    page_object_numbers = []

    objects.append("<< /Type /Catalog /Pages 2 0 R >>")
    objects.append("")

    for page_index, page_lines in enumerate(pages):
        page_obj_number = 3 + page_index * 2
        content_obj_number = page_obj_number + 1
        page_object_numbers.append(page_obj_number)

        text_commands = ["BT", "/F1 11 Tf", "50 780 Td", "14 TL"]
        for line_index, line in enumerate(page_lines):
            if line_index:
                text_commands.append("T*")
            text_commands.append(f"({_escape_pdf_text(line)}) Tj")
        text_commands.append("ET")
        stream = "\n".join(text_commands)

        objects.append(
            f"<< /Type /Page /Parent {pages_object_number} 0 R /MediaBox [0 0 612 792] "
            f"/Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> "
            f"/Contents {content_obj_number} 0 R >>"
        )
        objects.append(f"<< /Length {len(stream.encode('latin-1', errors='replace'))} >>\nstream\n{stream}\nendstream")

    kids = " ".join(f"{number} 0 R" for number in page_object_numbers)
    objects[1] = f"<< /Type /Pages /Kids [{kids}] /Count {len(page_object_numbers)} >>"

    pdf = ["%PDF-1.4\n"]
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(sum(len(part.encode("latin-1", errors="replace")) for part in pdf))
        pdf.append(f"{index} 0 obj\n{obj}\nendobj\n")

    xref_offset = sum(len(part.encode("latin-1", errors="replace")) for part in pdf)
    pdf.append(f"xref\n0 {len(objects) + 1}\n")
    pdf.append("0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.append(f"{offset:010d} 00000 n \n")
    pdf.append(
        "trailer\n"
        f"<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
        "startxref\n"
        f"{xref_offset}\n"
        "%%EOF"
    )

    return "".join(pdf).encode("latin-1", errors="replace")


def render_interactive_answer(question: str, final_answer: str, evaluation: dict) -> None:
    word_count = evaluation.get("word_count", len(final_answer.split())) if isinstance(evaluation, dict) else len(final_answer.split())
    score = evaluation.get("score", "N/A") if isinstance(evaluation, dict) else "N/A"
    missing_sections = evaluation.get("missing_sections", []) if isinstance(evaluation, dict) else []
    sections = split_assignment_sections(final_answer)

    metric_cols = st.columns(4)
    metric_cols[0].metric("Quality Score", score)
    metric_cols[1].metric("Word Count", word_count)
    metric_cols[2].metric("Sections", len(sections))
    metric_cols[3].metric("Missing", len(missing_sections))

    pdf_bytes = create_assignment_pdf(question, final_answer, evaluation)
    st.markdown(
        (
            '<div class="download-report-panel">'
            "<strong>Download report</strong>"
            "<p>Export the generated assignment with evaluation status, score, and word count as a PDF document.</p>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )
    st.download_button(
        "Download assignment as PDF",
        data=pdf_bytes,
        file_name="generated_assignment.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

    st.markdown("### Interactive Assignment View")
    if sections:
        for title, body in sections:
            with st.expander(title, expanded=title.lower() in {"overview", "introduction"}):
                st.markdown(body)
    else:
        st.markdown(final_answer)


st.set_page_config(
    page_title="Smart Assignment Helper",
    page_icon="AI",
    layout="wide",
)

with st.sidebar:
    st.markdown("## Settings")
    theme_mode = st.radio("Theme", ["Light", "Dark"], horizontal=True)
    selected_model = st.selectbox("Model selection", ["llama3", "phi3"], index=0)
    show_logs = st.toggle("Show debug state", value=False)
    st.markdown("---")
    st.info(
        "The interface shows the full multi-agent route while the existing backend runs the local Ollama pipeline."
    )
    st.caption(f"Selected UI model preference: {selected_model}")

inject_styles(theme_mode)

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
                    render_interactive_answer(question, final_answer, evaluation)

                with tabs[1]:
                    col_status, col_feedback = st.columns([1, 3])
                    with col_status:
                        if status == "Good":
                            st.success(f"Status: {status}")
                        else:
                            st.warning(f"Status: {status}")
                        if isinstance(evaluation, dict):
                            st.metric("Score", evaluation.get("score", "N/A"))
                            st.metric("Word Count", evaluation.get("word_count", "N/A"))

                    with col_feedback:
                        st.markdown("#### Evaluator Feedback")
                        st.write(feedback)
                        missing_sections = evaluation.get("missing_sections", []) if isinstance(evaluation, dict) else []
                        if missing_sections:
                            st.warning(f"Missing sections: {', '.join(missing_sections)}")
                        else:
                            st.success("All required sections are present.")

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

"""
IT Helpdesk Agent — Streamlit UI (Modern Redesign)
Reuses run_model_tool_loop from chat.py so CLI, eval evidence and UI
share the same agent loop.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from env_loader import load_lab_env
from providers import make_provider
from tools import TOOL_FUNCTIONS, load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version
from chat import run_model_tool_loop, json_text, trim_history

load_lab_env(ROOT)

# ── Page config (must come FIRST) ──────────────────────────────────────────────
st.set_page_config(
    page_title="IT Helpdesk Agent",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Base Reset ─────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── App Background ─────────────────────── */
.stApp {
    background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 40%, #16213e 100%);
    min-height: 100vh;
}

/* ── Sidebar ────────────────────────────── */
[data-testid="stSidebar"] {
    background: rgba(15, 15, 30, 0.85) !important;
    backdrop-filter: blur(20px);
    border-right: 1px solid rgba(99, 102, 241, 0.15);
}

[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}

[data-testid="stSidebarContent"] {
    padding: 1.5rem 1rem;
}

/* ── Header ─────────────────────────────── */
.app-header {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 1.5rem 0 0.5rem 0;
    margin-bottom: 0.25rem;
}

.app-logo {
    width: 42px;
    height: 42px;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    font-weight: 700;
    color: white;
    letter-spacing: -1px;
    flex-shrink: 0;
    box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
}

.app-title {
    font-size: 1.5rem;
    font-weight: 700;
    background: linear-gradient(135deg, #a5b4fc, #c4b5fd);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.5px;
}

/* ── Status Badge ───────────────────────── */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

.status-online {
    background: rgba(16, 185, 129, 0.15);
    color: #10b981;
    border: 1px solid rgba(16, 185, 129, 0.3);
}

.status-offline {
    background: rgba(239, 68, 68, 0.15);
    color: #ef4444;
    border: 1px solid rgba(239, 68, 68, 0.3);
}

/* ── Metric Cards ───────────────────────── */
.metric-row {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    margin: 1rem 0;
}

.metric-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(99, 102, 241, 0.12);
    border-radius: 12px;
    padding: 14px 16px;
    text-align: center;
    transition: all 0.2s ease;
}

.metric-card:hover {
    background: rgba(99, 102, 241, 0.08);
    border-color: rgba(99, 102, 241, 0.3);
    transform: translateY(-1px);
}

.metric-value {
    font-size: 1.6rem;
    font-weight: 700;
    color: #a5b4fc;
    line-height: 1;
}

.metric-label {
    font-size: 0.68rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-top: 4px;
    font-weight: 500;
}

/* ── Tool Trace Panel ───────────────────── */
.trace-container {
    background: rgba(10, 10, 25, 0.6);
    border: 1px solid rgba(99, 102, 241, 0.15);
    border-radius: 12px;
    padding: 16px;
    margin: 8px 0;
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    font-size: 0.78rem;
}

.trace-title {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #6366f1;
    font-weight: 600;
    margin-bottom: 10px;
    font-family: 'Inter', sans-serif;
}

.trace-row {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 6px 0;
    border-bottom: 1px solid rgba(255,255,255,0.04);
}

.trace-row:last-child {
    border-bottom: none;
}

.trace-tag {
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    white-space: nowrap;
    flex-shrink: 0;
}

.tag-call {
    background: rgba(99, 102, 241, 0.2);
    color: #a5b4fc;
    border: 1px solid rgba(99, 102, 241, 0.3);
}

.tag-ok {
    background: rgba(16, 185, 129, 0.15);
    color: #6ee7b7;
    border: 1px solid rgba(16, 185, 129, 0.25);
}

.tag-err {
    background: rgba(239, 68, 68, 0.15);
    color: #fca5a5;
    border: 1px solid rgba(239, 68, 68, 0.25);
}

.trace-content {
    color: #94a3b8;
    flex: 1;
    word-break: break-all;
    line-height: 1.5;
}

.trace-content strong {
    color: #e2e8f0;
}

/* ── Chat Messages ───────────────────────── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 0.25rem 0 !important;
}

.user-bubble {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(139, 92, 246, 0.1));
    border: 1px solid rgba(99, 102, 241, 0.2);
    border-radius: 16px 16px 4px 16px;
    padding: 12px 16px;
    color: #e2e8f0;
    font-size: 0.9rem;
    line-height: 1.6;
    max-width: 85%;
    margin-left: auto;
    margin-bottom: 4px;
    box-shadow: 0 2px 12px rgba(99, 102, 241, 0.1);
}

.agent-bubble {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 4px 16px 16px 16px;
    padding: 14px 18px;
    color: #cbd5e1;
    font-size: 0.9rem;
    line-height: 1.7;
    max-width: 90%;
    margin-bottom: 4px;
}

/* ── Info Banner ─────────────────────────── */
.info-banner {
    background: rgba(99, 102, 241, 0.08);
    border: 1px solid rgba(99, 102, 241, 0.2);
    border-radius: 12px;
    padding: 20px 24px;
    text-align: center;
    color: #94a3b8;
    font-size: 0.88rem;
    line-height: 1.6;
    margin: 2rem auto;
    max-width: 480px;
}

.info-banner strong {
    color: #a5b4fc;
}

/* ── Sidebar Tools List ──────────────────── */
.tool-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 0;
    color: #94a3b8;
    font-size: 0.8rem;
    border-bottom: 1px solid rgba(255,255,255,0.04);
}

.tool-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #6366f1;
    flex-shrink: 0;
}

/* ── Sidebar Section Label ───────────────── */
.sidebar-label {
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    color: #475569;
    font-weight: 600;
    margin: 1.2rem 0 0.6rem 0;
}

/* ── Artifact Version Display ────────────── */
.version-block {
    background: rgba(0,0,0,0.3);
    border-radius: 8px;
    padding: 10px 12px;
    font-family: monospace;
    font-size: 0.72rem;
    color: #64748b;
    line-height: 1.8;
    border: 1px solid rgba(255,255,255,0.05);
}

.version-block span {
    color: #a5b4fc;
}

/* ── Streamlit overrides ─────────────────── */
.stButton > button {
    background: rgba(99, 102, 241, 0.15) !important;
    border: 1px solid rgba(99, 102, 241, 0.3) !important;
    color: #a5b4fc !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    font-size: 0.82rem !important;
    transition: all 0.2s ease !important;
    padding: 0.45rem 1rem !important;
}

.stButton > button:hover {
    background: rgba(99, 102, 241, 0.28) !important;
    border-color: rgba(99, 102, 241, 0.55) !important;
    color: #c4b5fd !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2) !important;
}

.stButton > button:active {
    transform: translateY(0px) !important;
}

.stSelectbox > div > div {
    background: rgba(255,255,255,0.05) !important;
    border-color: rgba(99, 102, 241, 0.2) !important;
    color: #e2e8f0 !important;
    border-radius: 8px !important;
}

.stTextInput > div > div > input {
    background: rgba(255,255,255,0.05) !important;
    border-color: rgba(99, 102, 241, 0.2) !important;
    color: #e2e8f0 !important;
    border-radius: 8px !important;
    font-size: 0.85rem !important;
}

.stTextInput > div > div > input:focus {
    border-color: rgba(99, 102, 241, 0.5) !important;
    box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.1) !important;
}

[data-testid="stChatInput"] textarea {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(99, 102, 241, 0.2) !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
    font-size: 0.9rem !important;
    font-family: 'Inter', sans-serif !important;
}

[data-testid="stChatInput"] textarea:focus {
    border-color: rgba(99, 102, 241, 0.5) !important;
    box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.08) !important;
}

[data-testid="stChatInput"] button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    border-radius: 8px !important;
    border: none !important;
}

.stAlert {
    background: rgba(99, 102, 241, 0.08) !important;
    border: 1px solid rgba(99, 102, 241, 0.2) !important;
    border-radius: 10px !important;
    color: #94a3b8 !important;
}

.stDownloadButton > button {
    background: rgba(16, 185, 129, 0.12) !important;
    border: 1px solid rgba(16, 185, 129, 0.25) !important;
    color: #6ee7b7 !important;
    border-radius: 8px !important;
    font-size: 0.82rem !important;
}

hr {
    border-color: rgba(255,255,255,0.06) !important;
    margin: 1rem 0 !important;
}

.stSpinner > div {
    border-top-color: #6366f1 !important;
}

/* Remove streamlit branding */
#MainMenu, footer, header { visibility: hidden; }

/* Scrollbar */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(99, 102, 241, 0.3); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: rgba(99, 102, 241, 0.5); }

/* Expander */
.streamlit-expanderHeader {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 8px !important;
    color: #94a3b8 !important;
    font-size: 0.8rem !important;
}

[data-testid="stExpander"] {
    border: none !important;
}
</style>
""", unsafe_allow_html=True)


# ── Session State ───────────────────────────────────────────────────────────────
def init_session_state():
    defaults = {
        "messages": [],
        "tool_events": [],
        "transcript": {
            "transcript_id": f"ui_{datetime.now().strftime('%Y%m%dT%H%M%S%f')}",
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "turns": [],
        },
        "provider": None,
        "artifact_version": None,
        "system_prompt": None,
        "openai_tools": None,
        "selected_model": None,
        "filter_role": "All",
        "filter_has_tools": False,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


# ── Load Artifacts ─────────────────────────────────────────────────────────────
def load_artifacts(provider_name: str, model_name: str | None = None):
    artifacts_dir = ROOT / "artifacts"
    system_prompt_path = artifacts_dir / "system_prompt.md"
    tools_path = artifacts_dir / "tools.yaml"

    system_prompt = system_prompt_path.read_text(encoding="utf-8")
    tool_declarations = load_tool_declarations(tools_path)
    openai_tools = to_openai_tools(tool_declarations)
    provider = make_provider(provider_name)
    selected_model = model_name or getattr(provider, "default_model", None)
    artifact_version = build_artifact_version("v0", system_prompt_path, tools_path)

    return system_prompt, openai_tools, provider, selected_model, artifact_version


# ── Tool Trace Renderer ─────────────────────────────────────────────────────────
def render_tool_trace(tool_calls: list[dict], tool_results: list[dict]):
    if not tool_calls and not tool_results:
        return

    rows_html = ""

    for call in tool_calls:
        args_str = json.dumps(call.get("args", {}), ensure_ascii=False)
        if len(args_str) > 140:
            args_str = args_str[:140] + "…"
        rows_html += f"""
        <div class="trace-row">
            <span class="trace-tag tag-call">call</span>
            <span class="trace-content"><strong>{call['name']}</strong>&nbsp;&nbsp;{args_str}</span>
        </div>"""

    for res in tool_results:
        result_data = res.get("result", {})
        is_err = isinstance(result_data, dict) and "error" in result_data
        tag_cls = "tag-err" if is_err else "tag-ok"
        tag_label = "error" if is_err else "result"

        result_str = json.dumps(result_data, ensure_ascii=False, default=str)
        if len(result_str) > 200:
            result_str = result_str[:200] + "…"

        rows_html += f"""
        <div class="trace-row">
            <span class="trace-tag {tag_cls}">{tag_label}</span>
            <span class="trace-content"><strong>{res['tool']}</strong>&nbsp;&nbsp;{result_str}</span>
        </div>"""

    st.markdown(f"""
    <div class="trace-container">
        <div class="trace-title">Tool Trace</div>
        {rows_html}
    </div>""", unsafe_allow_html=True)


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    init_session_state()

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        is_ready = st.session_state.provider is not None
        status_cls = "status-online" if is_ready else "status-offline"
        status_dot = "●" if is_ready else "○"
        status_text = "Ready" if is_ready else "Offline"

        st.markdown(f"""
        <div class="app-header">
            <div class="app-logo">IT</div>
            <div>
                <div class="app-title">Helpdesk Agent</div>
                <span class="status-badge {status_cls}">{status_dot}&nbsp;{status_text}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="sidebar-label">Provider</div>', unsafe_allow_html=True)

        provider_name = st.selectbox(
            "Provider",
            ["openai", "openrouter", "anthropic", "gemini"],
            label_visibility="collapsed",
        )

        model_name = st.text_input(
            "Model (leave blank for default)",
            value="",
            placeholder="e.g. gpt-4o-mini",
        ) or None

        st.markdown('<div class="sidebar-label">Parameters</div>', unsafe_allow_html=True)

        history_window = st.slider("History window", 1, 20, 5,
                                   help="Recent message pairs kept in context")
        max_tool_rounds = st.slider("Max tool rounds", 1, 10, 4,
                                    help="Max tool calling rounds per turn")

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        col_load, col_clear = st.columns(2)
        with col_load:
            if st.button("Load", use_container_width=True):
                try:
                    sp, tools, prov, model, av = load_artifacts(provider_name, model_name)
                    st.session_state.system_prompt = sp
                    st.session_state.openai_tools = tools
                    st.session_state.provider = prov
                    st.session_state.selected_model = model
                    st.session_state.artifact_version = av
                    st.success("Artifacts loaded.")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

        with col_clear:
            if st.button("Clear", use_container_width=True):
                st.session_state.messages = []
                st.session_state.tool_events = []
                st.session_state.transcript = {
                    "transcript_id": f"ui_{datetime.now().strftime('%Y%m%dT%H%M%S%f')}",
                    "created_at": datetime.now().isoformat(timespec="seconds"),
                    "turns": [],
                }
                st.rerun()

        # Artifact version
        if st.session_state.artifact_version:
            av = st.session_state.artifact_version
            st.markdown('<div class="sidebar-label">Artifact</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="version-block">
                version&nbsp;&nbsp;<span>{av.artifact_version}</span><br>
                prompt&nbsp;&nbsp;&nbsp;<span>{av.prompt_hash[:14]}…</span><br>
                tools&nbsp;&nbsp;&nbsp;&nbsp;<span>{av.tools_hash[:14]}…</span>
            </div>""", unsafe_allow_html=True)

        # Available tools
        st.markdown('<div class="sidebar-label">Available Tools</div>', unsafe_allow_html=True)
        tools_html = "".join(
            f'<div class="tool-item"><div class="tool-dot"></div>{name}</div>'
            for name in TOOL_FUNCTIONS.keys()
        )
        st.markdown(tools_html, unsafe_allow_html=True)

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        # Download transcript
        if st.session_state.transcript["turns"]:
            transcript_json = json.dumps(
                st.session_state.transcript, ensure_ascii=False, indent=2
            )
            st.download_button(
                label="Download Transcript",
                data=transcript_json,
                file_name=f"{st.session_state.transcript['transcript_id']}.json",
                mime="application/json",
                use_container_width=True,
            )

    # ── Main content ──────────────────────────────────────────────────────────
    if st.session_state.provider is None:
        st.markdown("""
        <div class="info-banner">
            <strong>No provider loaded</strong><br>
            Select a provider in the sidebar and click <strong>Load</strong> to start the session.
        </div>
        """, unsafe_allow_html=True)
        return

    # Metrics
    turns_total = len(st.session_state.transcript["turns"])
    tool_total  = len(st.session_state.tool_events)
    last_status = "—"
    if st.session_state.transcript["turns"]:
        last_status = st.session_state.transcript["turns"][-1].get("status", "—")

    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-card">
            <div class="metric-value">{turns_total}</div>
            <div class="metric-label">Turns</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{tool_total}</div>
            <div class="metric-label">Tool Events</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{last_status}</div>
            <div class="metric-label">Last Status</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Filters
    st.markdown('<div class="sidebar-label" style="margin-top:0.4rem">Filter</div>',
                unsafe_allow_html=True)

    fc1, fc2, fc3, fc4 = st.columns([1, 1, 1, 3])
    with fc1:
        active = st.session_state.filter_role == "All"
        if st.button(("▸ " if active else "") + "All", use_container_width=True):
            st.session_state.filter_role = "All"
            st.rerun()
    with fc2:
        active = st.session_state.filter_role == "User"
        if st.button(("▸ " if active else "") + "You", use_container_width=True):
            st.session_state.filter_role = "User"
            st.rerun()
    with fc3:
        active = st.session_state.filter_role == "Agent"
        if st.button(("▸ " if active else "") + "Agent", use_container_width=True):
            st.session_state.filter_role = "Agent"
            st.rerun()
    with fc4:
        st.session_state.filter_has_tools = st.toggle(
            "Only turns with tool calls",
            value=st.session_state.filter_has_tools,
        )

    st.markdown("<hr>", unsafe_allow_html=True)

    # Chat history
    for message in st.session_state.messages:
        role = message["role"]

        # Role filter
        if st.session_state.filter_role == "User" and role != "user":
            continue
        if st.session_state.filter_role == "Agent" and role != "assistant":
            continue

        # Tool-calls-only filter
        if st.session_state.filter_has_tools and role == "assistant":
            has_tools = bool(message.get("tool_calls")) or bool(message.get("tool_results"))
            if not has_tools:
                continue

        with st.chat_message(role):
            if role == "user":
                st.markdown(
                    f'<div class="user-bubble">{message["content"]}</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div class="agent-bubble">{message["content"]}</div>',
                    unsafe_allow_html=True,
                )
                tc = message.get("tool_calls", [])
                tr = message.get("tool_results", [])
                if tc or tr:
                    with st.expander(
                        f"Tool trace  ·  {len(tc)} call(s)  ·  {len(tr)} result(s)"
                    ):
                        render_tool_trace(tc, tr)

    # Chat input
    if prompt := st.chat_input("Ask about VPN, devices, users, policies, tickets…"):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(
                f'<div class="user-bubble">{prompt}</div>',
                unsafe_allow_html=True,
            )

        # Build context
        history = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages[:-1]
        ]
        messages = [
            {"role": "system", "content": st.session_state.system_prompt},
            *trim_history(history, history_window),
            {"role": "user", "content": prompt},
        ]

        with st.chat_message("assistant"):
            with st.spinner("Processing…"):
                try:
                    result = run_model_tool_loop(
                        provider=st.session_state.provider,
                        messages=messages,
                        tools=st.session_state.openai_tools,
                        model=st.session_state.selected_model,
                        max_tool_rounds=max_tool_rounds,
                    )

                    assistant_text = result.get("assistant_text", "")
                    rounds         = result.get("rounds", [])
                    tool_events    = result.get("tool_events", [])

                    all_tool_calls   = []
                    all_tool_results = []
                    for rd in rounds:
                        all_tool_calls.extend(rd.get("tool_calls", []))
                        all_tool_results.extend(rd.get("tool_results", []))

                    st.markdown(
                        f'<div class="agent-bubble">{assistant_text}</div>',
                        unsafe_allow_html=True,
                    )

                    if all_tool_calls or all_tool_results:
                        with st.expander(
                            f"Tool trace  ·  {len(all_tool_calls)} call(s)"
                            f"  ·  {len(all_tool_results)} result(s)"
                        ):
                            render_tool_trace(all_tool_calls, all_tool_results)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": assistant_text,
                        "tool_calls": all_tool_calls,
                        "tool_results": all_tool_results,
                    })
                    st.session_state.tool_events.extend(tool_events)

                    st.session_state.transcript["turns"].append({
                        "turn_index": len(st.session_state.transcript["turns"]) + 1,
                        "started_at": datetime.now().isoformat(timespec="seconds"),
                        "user": prompt,
                        "assistant_text": assistant_text,
                        "rounds": rounds,
                        "tool_events": tool_events,
                        "status": result.get("status", "unknown"),
                    })
                    st.session_state.transcript["updated_at"] = (
                        datetime.now().isoformat(timespec="seconds")
                    )

                except Exception as e:
                    err = f"{type(e).__name__}: {e}"
                    st.error(err)
                    st.session_state.messages.append({"role": "assistant", "content": err})


if __name__ == "__main__":
    main()
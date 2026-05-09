"""
components/theme.py — Dynamic CSS injection for dark/light mode in QueryWise.
"""

import streamlit as st

DARK_CSS = """
<style>
    /* ── Global reset & fonts ──────────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Sora', sans-serif !important;
    }
    code, pre, .stCode {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* ── Background & surface ──────────────────────────────────────────── */
    .stApp {
        background: #0d0f14 !important;
        color: #e2e8f0 !important;
    }
    section[data-testid="stSidebar"] {
        background: #13161e !important;
        border-right: 1px solid rgba(255,255,255,0.06) !important;
    }

    /* ── Buttons ────────────────────────────────────────────────────────── */
    .stButton > button {
        background: #1e2130 !important;
        color: #e2e8f0 !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 8px !important;
        font-family: 'Sora', sans-serif !important;
        font-size: 0.82rem !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        background: #252a3a !important;
        border-color: rgba(99,179,237,0.4) !important;
        color: #90cdf4 !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
        color: #fff !important;
        border: none !important;
        font-weight: 600 !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
        box-shadow: 0 4px 15px rgba(37,99,235,0.35) !important;
    }

    /* ── Inputs ─────────────────────────────────────────────────────────── */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: #1a1d27 !important;
        color: #e2e8f0 !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 8px !important;
        font-family: 'Sora', sans-serif !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 2px rgba(37,99,235,0.2) !important;
    }

    /* ── Chat messages ──────────────────────────────────────────────────── */
    .stChatMessage {
        background: #161923 !important;
        border: 1px solid rgba(255,255,255,0.05) !important;
        border-radius: 12px !important;
        margin-bottom: 0.75rem !important;
    }

    /* ── Code blocks ─────────────────────────────────────────────────────── */
    .stCode {
        background: #0f1117 !important;
        border: 1px solid rgba(99,179,237,0.2) !important;
        border-radius: 8px !important;
    }

    /* ── Expanders ────────────────────────────────────────────────────────── */
    .streamlit-expanderHeader {
        background: #1a1d27 !important;
        border-radius: 8px !important;
        color: #e2e8f0 !important;
    }

    /* ── Divider ─────────────────────────────────────────────────────────── */
    hr {
        border-color: rgba(255,255,255,0.06) !important;
    }

    /* ── Success / Error / Warning ───────────────────────────────────────── */
    .stSuccess {
        background: rgba(16,185,129,0.12) !important;
        border: 1px solid rgba(16,185,129,0.3) !important;
        color: #6ee7b7 !important;
        border-radius: 8px !important;
    }
    .stError {
        background: rgba(239,68,68,0.1) !important;
        border: 1px solid rgba(239,68,68,0.3) !important;
        color: #fca5a5 !important;
        border-radius: 8px !important;
    }

    /* ── Dataframe ───────────────────────────────────────────────────────── */
    .stDataFrame {
        border: 1px solid rgba(255,255,255,0.07) !important;
        border-radius: 10px !important;
    }

    /* ── Scrollbar ───────────────────────────────────────────────────────── */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.12); border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.22); }
</style>
"""

LIGHT_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Sora', sans-serif !important;
    }
    code, pre, .stCode {
        font-family: 'JetBrains Mono', monospace !important;
    }

    .stApp {
        background: #f5f7fa !important;
        color: #1a202c !important;
    }
    section[data-testid="stSidebar"] {
        background: #ffffff !important;
        border-right: 1px solid rgba(0,0,0,0.08) !important;
    }

    .stButton > button {
        background: #ffffff !important;
        color: #1a202c !important;
        border: 1px solid rgba(0,0,0,0.12) !important;
        border-radius: 8px !important;
        font-family: 'Sora', sans-serif !important;
        font-size: 0.82rem !important;
    }
    .stButton > button:hover {
        background: #eef2ff !important;
        border-color: #2563eb !important;
        color: #2563eb !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
        color: #fff !important;
        border: none !important;
        font-weight: 600 !important;
    }

    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: #ffffff !important;
        color: #1a202c !important;
        border: 1px solid rgba(0,0,0,0.15) !important;
        border-radius: 8px !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 2px rgba(37,99,235,0.15) !important;
    }

    .stChatMessage {
        background: #ffffff !important;
        border: 1px solid rgba(0,0,0,0.07) !important;
        border-radius: 12px !important;
        margin-bottom: 0.75rem !important;
    }

    .stCode {
        background: #f8f9fc !important;
        border: 1px solid rgba(37,99,235,0.2) !important;
        border-radius: 8px !important;
    }

    hr {
        border-color: rgba(0,0,0,0.07) !important;
    }

    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.15); border-radius: 4px; }
</style>
"""


def apply_theme():
    """Inject CSS for the currently selected theme."""
    theme = st.session_state.get("theme", "dark")
    st.markdown(DARK_CSS if theme == "dark" else LIGHT_CSS, unsafe_allow_html=True)

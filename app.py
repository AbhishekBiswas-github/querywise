"""
app.py — QueryWise: AI-Powered SQL Intelligence Platform
Entry point for the Streamlit application.
"""

import streamlit as st

# ── Page config (must be first Streamlit call) ─────────────────────────────
st.set_page_config(
    page_title="QueryWise · AI SQL Intelligence",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Internal imports (after set_page_config) ───────────────────────────────
from components.theme import apply_theme
from components.sidebar import render_sidebar
from components.schema_explorer import render_schema_explorer
from components.chat import render_chat
from utils.db import connect_to_database, get_tables, extract_table_info
from utils.vector_store import build_collection
from utils.llm import get_llm


def initialise_session():
    """Set sensible defaults for session state keys."""
    defaults = {
        "theme": "dark",
        "db_connected": False,
        "db_error": None,
        "messages": [],
        "api_key": "",
        "db_host": "localhost",
        "db_user": "root",
        "db_password": "",
        "db_name": "",
        "n_results": 4,
        "auto_execute": False,
        "show_raw_sql": True,
        "active_tab": "explorer",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def handle_connection(connect_clicked: bool):
    """
    If the Connect button was clicked, attempt to connect to MySQL,
    extract schema, build the vector store, and initialise the LLM.
    """
    if not connect_clicked:
        return

    api_key = st.session_state.get("api_key", "").strip()
    host = st.session_state.get("db_host", "").strip()
    user = st.session_state.get("db_user", "").strip()
    password = st.session_state.get("db_password", "")
    database = st.session_state.get("db_name", "").strip()

    # Validate inputs
    if not api_key:
        st.session_state["db_error"] = "Groq API key is required."
        st.session_state["db_connected"] = False
        return
    if not database:
        st.session_state["db_error"] = "Database name cannot be empty."
        st.session_state["db_connected"] = False
        return

    with st.spinner("Connecting to database and building schema index…"):
        conn, err = connect_to_database(host, user, password, database)

        if err:
            st.session_state["db_connected"] = False
            st.session_state["db_error"] = err
            return

        # Success: store connection and build schema vector store
        st.session_state["conn"] = conn
        tables = get_tables(conn)
        st.session_state["tables"] = tables

        table_info = extract_table_info(conn, tables, database)
        collection = build_collection(
            table_info,
            collection_name=f"schema_{database}",
        )
        st.session_state["collection"] = collection
        st.session_state["llm"] = get_llm(api_key)

        st.session_state["db_connected"] = True
        st.session_state["db_error"] = None
        # Reset chat on new connection
        st.session_state["messages"] = []


def render_welcome():
    """Landing screen shown before connection."""
    st.markdown(
        """
        <div style="text-align:center; padding: 4rem 2rem;">
            <div style="font-size:4rem; margin-bottom:1rem;">🔍</div>
            <h1 style="font-size:2.5rem; font-weight:700; letter-spacing:-1px; margin-bottom:0.5rem;">
                Welcome to QueryWise
            </h1>
            <p style="font-size:1.1rem; opacity:0.55; max-width:520px; margin:0 auto 2rem;">
                Your AI-powered SQL intelligence platform. Connect your MySQL database
                and start querying in plain English.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    features = [
        ("🧠", "Natural Language SQL", "Describe what you want — get production-ready SQL instantly."),
        ("🗂️", "Schema Explorer", "Browse tables, columns, and relationships at a glance."),
        ("⚡", "Instant Execution", "Optionally run queries directly and see results in-app."),
    ]
    for col, (icon, title, desc) in zip([col1, col2, col3], features):
        with col:
            st.markdown(
                f"""
                <div style="
                    border: 1px solid rgba(128,128,128,0.2);
                    border-radius: 12px;
                    padding: 1.5rem;
                    text-align: center;
                ">
                    <div style="font-size:2rem; margin-bottom:0.75rem;">{icon}</div>
                    <h4 style="margin:0 0 0.5rem; font-size:1rem;">{title}</h4>
                    <p style="margin:0; font-size:0.85rem; opacity:0.55;">{desc}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown(
        "<p style='text-align:center; opacity:0.4; margin-top:2.5rem; font-size:0.85rem;'>"
        "Enter your Groq API key and database credentials in the sidebar to get started."
        "</p>",
        unsafe_allow_html=True,
    )


def main():
    initialise_session()
    apply_theme()

    # Render sidebar and capture connect click
    connect_clicked = render_sidebar()

    # Handle connection logic
    handle_connection(connect_clicked)

    # ── Main content area ──────────────────────────────────────────────────
    if not st.session_state.get("db_connected"):
        render_welcome()
    else:
        conn = st.session_state["conn"]
        tables = st.session_state["tables"]

        # Tab navigation
        tab_explorer, tab_chat, tab_history = st.tabs(
            ["📊 Schema Explorer", "💬 Chat with AI", "📜 Query History"]
        )

        with tab_explorer:
            render_schema_explorer(conn, tables)

        with tab_chat:
            render_chat()

        with tab_history:
            render_query_history()


def render_query_history():
    """Display all SQL queries generated in this session."""
    st.markdown("## 📜 Query History")
    messages = st.session_state.get("messages", [])
    sql_messages = [m for m in messages if m["role"] == "assistant" and "```sql" in m.get("content", "")]

    if not sql_messages:
        st.info("No SQL queries generated yet. Head to the Chat tab to get started!")
        return

    for i, msg in enumerate(reversed(sql_messages), 1):
        content = msg["content"]
        parts = content.split("```sql")
        if len(parts) > 1:
            sql_part = parts[1].split("```")[0].strip()
            with st.expander(f"Query #{len(sql_messages) - i + 1}", expanded=(i == 1)):
                st.code(sql_part, language="sql")

                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button(f"▶ Run", key=f"run_hist_{i}") and st.session_state.get("conn"):
                        from utils.db import execute_sql
                        df, err = execute_sql(st.session_state["conn"], sql_part)
                        if err:
                            st.error(f"Error: {err}")
                        else:
                            st.dataframe(df, use_container_width=True)
                            st.caption(f"Returned {len(df)} row(s)")


if __name__ == "__main__":
    main()

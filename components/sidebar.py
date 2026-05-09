"""
components/sidebar.py — Sidebar UI for QueryWise: credentials, connection, and settings.
"""

import streamlit as st


def render_sidebar():
    """
    Render the sidebar and return a dict of user-provided configuration.
    Mutates st.session_state for connection status.
    """
    with st.sidebar:
        # ── Brand ──────────────────────────────────────────────────────────
        st.markdown(
            """
            <div style="text-align:center; padding: 1rem 0 1.5rem;">
                <span style="font-size:2rem;">🔍</span>
                <h2 style="margin:0.25rem 0 0; font-size:1.4rem; font-weight:700; letter-spacing:-0.5px;">
                    QueryWise
                </h2>
                <p style="margin:0; font-size:0.75rem; opacity:0.55; letter-spacing:0.08em; text-transform:uppercase;">
                    AI-Powered SQL Intelligence
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()

        # ── Theme toggle ───────────────────────────────────────────────────
        st.markdown("#### ⚙️ Appearance")
        theme = st.radio(
            "Color theme",
            options=["🌙 Dark", "☀️ Light"],
            index=0 if st.session_state.get("theme", "dark") == "dark" else 1,
            horizontal=True,
            label_visibility="collapsed",
        )
        st.session_state["theme"] = "dark" if "Dark" in theme else "light"

        st.divider()

        # ── API Key ────────────────────────────────────────────────────────
        st.markdown("#### 🔑 Groq API Key")
        api_key = st.text_input(
            "Groq API Key",
            type="password",
            placeholder="gsk_••••••••••••••••••••",
            value=st.session_state.get("api_key", ""),
            label_visibility="collapsed",
        )
        st.session_state["api_key"] = api_key

        st.divider()

        # ── Database credentials ───────────────────────────────────────────
        st.markdown("#### 🗄️ Database Connection")

        host = st.text_input(
            "Host",
            value=st.session_state.get("db_host", "localhost"),
            placeholder="localhost",
        )
        col1, col2 = st.columns(2)
        with col1:
            user = st.text_input(
                "User",
                value=st.session_state.get("db_user", "root"),
                placeholder="root",
            )
        with col2:
            password = st.text_input(
                "Password",
                type="password",
                value=st.session_state.get("db_password", ""),
                placeholder="••••••••",
            )
        database = st.text_input(
            "Database Name",
            value=st.session_state.get("db_name", ""),
            placeholder="ecommerce_db",
        )

        # Save to session
        st.session_state["db_host"] = host
        st.session_state["db_user"] = user
        st.session_state["db_password"] = password
        st.session_state["db_name"] = database

        # ── Connect button ─────────────────────────────────────────────────
        connect_clicked = st.button("⚡ Connect to Database", use_container_width=True, type="primary")

        # Connection status badge
        if st.session_state.get("db_connected"):
            st.success(f"✅ Connected — **{st.session_state.get('db_name')}**")
        elif st.session_state.get("db_error"):
            st.error(f"❌ {st.session_state['db_error']}")

        st.divider()

        # ── Advanced settings ──────────────────────────────────────────────
        with st.expander("🛠️ Advanced Settings"):
            st.session_state["n_results"] = st.slider(
                "Schema context chunks (RAG)",
                min_value=1,
                max_value=10,
                value=st.session_state.get("n_results", 4),
                help="How many schema chunks to retrieve for each query.",
            )
            st.session_state["auto_execute"] = st.toggle(
                "Auto-execute generated SQL",
                value=st.session_state.get("auto_execute", False),
                help="Automatically run the SQL against the database and show results.",
            )
            st.session_state["show_raw_sql"] = st.toggle(
                "Always show formatted SQL",
                value=st.session_state.get("show_raw_sql", True),
            )

        st.divider()

        # ── Session controls ───────────────────────────────────────────────
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state["messages"] = []
                st.rerun()
        with col_b:
            if st.button("🔌 Disconnect", use_container_width=True):
                for key in ["db_connected", "db_error", "conn", "tables", "collection", "llm"]:
                    st.session_state.pop(key, None)
                st.rerun()

        st.markdown(
            "<div style='text-align:center; opacity:0.35; font-size:0.7rem; padding-top:1rem;'>"
            "QueryWise v1.0 · Built with ❤️</div>",
            unsafe_allow_html=True,
        )

    return connect_clicked

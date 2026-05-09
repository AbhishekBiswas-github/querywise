"""
components/chat.py — Conversational chat interface for QueryWise.
"""

import streamlit as st
import pandas as pd
from utils.vector_store import query_collection
from utils.llm import generate_sql, generate_chat_response
from utils.db import execute_sql


# Suggested starter prompts
EXAMPLE_PROMPTS = [
    "Show me all table relationships",
    "Query for top 10 customers by total spending",
    "Find products with low inventory",
    "Show monthly revenue trend",
    "List all orders placed in the last 30 days",
    "Which categories have the most products?",
]


def _build_history_string(messages: list[dict], max_turns: int = 6) -> str:
    """Convert recent chat history to a plain-text string for the LLM."""
    recent = messages[-max_turns * 2 :]
    lines = []
    for m in recent:
        role = "User" if m["role"] == "user" else "Assistant"
        # Strip code blocks for brevity in context
        content = m["content"]
        lines.append(f"{role}: {content}")
    return "\n".join(lines)


def _render_message(msg: dict):
    """Render a single chat message with special handling for SQL."""
    with st.chat_message(msg["role"], avatar="🧑" if msg["role"] == "user" else "🔍"):
        content = msg["content"]

        # Detect embedded SQL code blocks and render them nicely
        if "```sql" in content:
            parts = content.split("```sql")
            st.markdown(parts[0])
            for part in parts[1:]:
                sql_end = part.find("```")
                if sql_end != -1:
                    sql_code = part[:sql_end].strip()
                    after = part[sql_end + 3 :]
                    st.code(sql_code, language="sql")

                    # Auto-execute toggle
                    if st.session_state.get("auto_execute") and st.session_state.get("conn"):
                        _run_sql_inline(sql_code)

                    if after.strip():
                        st.markdown(after)
        else:
            st.markdown(content)

        # Render any stored result DataFrame
        if msg.get("result_df") is not None:
            df: pd.DataFrame = msg["result_df"]
            st.dataframe(df, use_container_width=True)
            st.caption(f"Query returned {len(df)} row(s)")


def _run_sql_inline(sql: str):
    """Execute SQL and display results inline."""
    conn = st.session_state.get("conn")
    if conn is None:
        st.warning("No active database connection.")
        return
    df, err = execute_sql(conn, sql)
    if err:
        st.error(f"SQL Error: {err}")
    else:
        st.dataframe(df, use_container_width=True)
        st.caption(f"Returned {len(df)} row(s)")


def render_chat():
    """Render the full chat interface."""
    st.markdown("## 💬 Ask QueryWise")
    st.markdown(
        "Chat naturally with your database. Ask for SQL queries, data insights, "
        "schema explanations, and more."
    )

    # Initialise message history
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    # ── Example prompt chips ───────────────────────────────────────────────
    if not st.session_state["messages"]:
        st.markdown("**✨ Try one of these:**")
        cols = st.columns(3)
        for i, prompt in enumerate(EXAMPLE_PROMPTS):
            with cols[i % 3]:
                if st.button(prompt, key=f"example_{i}", use_container_width=True):
                    st.session_state["pending_prompt"] = prompt
                    st.rerun()

        st.divider()

    # ── Render existing messages ───────────────────────────────────────────
    for msg in st.session_state["messages"]:
        _render_message(msg)

    # ── Chat input ─────────────────────────────────────────────────────────
    user_input = st.chat_input("Ask anything about your database…")

    # Handle example chip selection
    if st.session_state.get("pending_prompt"):
        user_input = st.session_state.pop("pending_prompt")

    if user_input:
        # Validate prerequisites
        if not st.session_state.get("api_key"):
            st.error("Please provide your Groq API key in the sidebar.")
            return
        if not st.session_state.get("db_connected"):
            st.error("Please connect to a database first.")
            return

        # Add user message
        st.session_state["messages"].append({"role": "user", "content": user_input})

        llm = st.session_state.get("llm")
        collection = st.session_state.get("collection")
        n_results = st.session_state.get("n_results", 4)

        # Retrieve relevant schema context
        context = query_collection(collection, user_input, n_results=n_results)

        # Build conversation history
        history = _build_history_string(st.session_state["messages"][:-1])

        # Generate response
        with st.spinner("QueryWise is thinking…"):
            # Decide: pure SQL request vs conversational
            sql_keywords = ["query", "sql", "select", "show me", "find", "list", "get", "how many", "count", "sum", "average", "top", "bottom"]
            is_sql_request = any(kw in user_input.lower() for kw in sql_keywords)

            if is_sql_request:
                raw_sql, formatted_sql = generate_sql(llm, user_input, context)

                # Build assistant response
                response_content = f"Here's the SQL query for your request:\n\n```sql\n{formatted_sql}\n```"

                # Append message
                msg = {"role": "assistant", "content": response_content, "result_df": None}

                # Auto-execute if enabled
                if st.session_state.get("auto_execute") and st.session_state.get("conn"):
                    df, err = execute_sql(st.session_state["conn"], raw_sql)
                    if err:
                        response_content += f"\n\n⚠️ **Execution error:** `{err}`"
                        msg["content"] = response_content
                    else:
                        msg["result_df"] = df

            else:
                response_text = generate_chat_response(llm, user_input, context, history)
                msg = {"role": "assistant", "content": response_text, "result_df": None}

        st.session_state["messages"].append(msg)
        st.rerun()

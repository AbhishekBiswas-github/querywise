"""
components/schema_explorer.py — Schema overview panel for QueryWise.
"""

import streamlit as st
from utils.db import preview_table, get_table_row_counts


def render_schema_explorer(conn, tables: list[str]):
    """Render an expandable schema explorer with table previews."""

    st.markdown("## 📊 Database Explorer")
    st.markdown(
        f"Connected to **`{st.session_state.get('db_name')}`** · "
        f"**{len(tables)}** table(s) found"
    )

    # Row counts
    with st.spinner("Loading table statistics…"):
        counts = get_table_row_counts(conn, tables)

    # Display table cards in a responsive grid
    cols_per_row = 3
    rows = [tables[i : i + cols_per_row] for i in range(0, len(tables), cols_per_row)]

    for row in rows:
        cols = st.columns(len(row))
        for col, table in zip(cols, row):
            with col:
                count = counts.get(table, -1)
                count_label = f"{count:,}" if count >= 0 else "N/A"
                st.markdown(
                    f"""
                    <div style="
                        border: 1px solid rgba(128,128,128,0.25);
                        border-radius: 10px;
                        padding: 1rem;
                        margin-bottom: 0.5rem;
                        text-align: center;
                    ">
                        <div style="font-size:1.4rem;">🗂️</div>
                        <div style="font-weight:700; font-size:0.95rem; margin:0.3rem 0;">{table}</div>
                        <div style="font-size:0.75rem; opacity:0.55;">{count_label} rows</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.divider()

    # Expandable table previews
    st.markdown("### 🔎 Table Previews")
    for table in tables:
        with st.expander(f"📋 `{table}`", expanded=False):
            try:
                df = preview_table(conn, table, limit=5)
                st.dataframe(df, use_container_width=True)
                st.caption(f"Showing first 5 rows of `{table}`")
            except Exception as e:
                st.error(f"Could not preview `{table}`: {e}")

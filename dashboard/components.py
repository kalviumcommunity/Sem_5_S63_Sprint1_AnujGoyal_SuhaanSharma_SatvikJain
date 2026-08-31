"""
Reusable UI Components for the Streamlit Dashboard.
"""

import streamlit as st


def render_header(title: str, subtitle: str) -> None:
    """Renders a standard application header."""
    st.title(title)
    st.caption(subtitle)
    st.divider()


def render_kpi_card(title: str, value: str, delta: str = None) -> None:
    """Renders a standard KPI metric card."""
    st.metric(label=title, value=value, delta=delta)

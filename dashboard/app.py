"""
Main Streamlit Application
Learning Behaviour & Course Completion Intelligence Dashboard
"""

import streamlit as st
from dashboard.components import render_header, render_kpi_summary_grid
from src.analysis import get_business_kpis


def main() -> None:
    st.set_page_config(
        page_title="Learning Behaviour & Course Completion Intelligence",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    render_header(
        title="🎓 Learning Behaviour & Course Completion Intelligence",
        subtitle="Predictive insights on student engagement, drop-off risk, and course completion."
    )

    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select View",
        ["Overview", "Engagement & Behaviour", "Risk & Drop-off Detection", "SQL Analytics"]
    )

    # Fetch live business KPIs from SQL analytics layer or fallback defaults
    try:
        kpi_data = get_business_kpis()
    except Exception:
        kpi_data = {}

    # Render 6 core summary KPI cards
    render_kpi_summary_grid(kpi_data, columns=6)

    st.divider()
    st.info(f"Currently viewing: **{page}**. Project analytics pipeline initialized successfully.")


if __name__ == "__main__":
    main()

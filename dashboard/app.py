"""
Main Streamlit Application
Learning Behaviour & Course Completion Intelligence Dashboard
"""

import streamlit as st
from dashboard.components import render_header, render_kpi_card


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

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_kpi_card("Active Students", "1,250", "+12%")
    with col2:
        render_kpi_card("Completion Rate", "68.4%", "+3.2%")
    with col3:
        render_kpi_card("Avg. Weekly Study Hours", "4.8 hrs", "+0.5 hrs")
    with col4:
        render_kpi_card("At-Risk Dropouts", "42", "-5")

    st.info(f"Currently viewing: **{page}**. Project workspace initialized successfully.")


if __name__ == "__main__":
    main()

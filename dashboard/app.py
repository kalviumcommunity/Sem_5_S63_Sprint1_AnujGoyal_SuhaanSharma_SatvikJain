"""
Main Streamlit Application
Learning Behaviour & Course Completion Intelligence Data Product
"""

import streamlit as st
from dashboard.components import render_header
from dashboard.views import (
    view_overview,
    view_student_behaviour,
    view_course_analytics,
    view_dropout_risk,
    view_behaviour_trends,
    view_sql_insights,
    view_reports
)


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
        [
            "Overview",
            "Student Behaviour",
            "Course Analytics",
            "Dropout Risk",
            "Behaviour Trends",
            "SQL Insights",
            "Reports"
        ]
    )

    # Route to view handler
    if page == "Overview":
        view_overview()
    elif page == "Student Behaviour":
        view_student_behaviour()
    elif page == "Course Analytics":
        view_course_analytics()
    elif page == "Dropout Risk":
        view_dropout_risk()
    elif page == "Behaviour Trends":
        view_behaviour_trends()
    elif page == "SQL Insights":
        view_sql_insights()
    elif page == "Reports":
        view_reports()


if __name__ == "__main__":
    main()

"""
Main Streamlit Application
Learning Behaviour & Course Completion Intelligence Data Product
"""

import streamlit as st
from dashboard.components import render_header
from dashboard.filters import filter_dashboard_views, render_filter_sidebar
from src.database import execute_analytical_views
from dashboard.views import (
    view_overview,
    view_student_behaviour,
    view_course_analytics,
    view_dropout_risk,
    view_behaviour_trends,
    view_sql_insights,
    view_reports,
    view_dataset_upload
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
            "Reports",
            "Dataset Upload"
        ]
    )

    if page == "Dataset Upload":
        view_dataset_upload()
    else:
        try:
            raw_views = execute_analytical_views()
        except Exception:
            raw_views = {}
        filters = render_filter_sidebar(raw_views)
        filtered_views = filter_dashboard_views(raw_views, filters)

        if page == "Overview":
            view_overview(views=filtered_views, filters=filters)
        elif page == "Student Behaviour":
            view_student_behaviour(views=filtered_views, filters=filters)
        elif page == "Course Analytics":
            view_course_analytics(views=filtered_views, filters=filters)
        elif page == "Dropout Risk":
            view_dropout_risk(views=filtered_views, filters=filters)
        elif page == "Behaviour Trends":
            view_behaviour_trends(views=filtered_views, filters=filters)
        elif page == "SQL Insights":
            view_sql_insights(views=filtered_views, filters=filters)
        elif page == "Reports":
            view_reports(views=filtered_views, filters=filters)


if __name__ == "__main__":
    main()

"""
Main Streamlit Application
Learning Behaviour & Course Completion Intelligence Data Product
"""

import streamlit as st
from dashboard.components import render_header
from dashboard.filters import filter_dashboard_views, render_filter_sidebar
from dashboard.state import PAGE_KEY, initialize_session_state
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


DATA_UPLOAD_PAGE = "Data Upload"
NAVIGATION_PAGES = (
    "Overview",
    "Student Behaviour",
    "Course Analytics",
    "Dropout Risk",
    "Behaviour Trends",
    "SQL Insights",
    "Reports",
)

PAGE_VIEWS = {
    "Overview": view_overview,
    "Student Behaviour": view_student_behaviour,
    "Course Analytics": view_course_analytics,
    "Dropout Risk": view_dropout_risk,
    "Behaviour Trends": view_behaviour_trends,
    "SQL Insights": view_sql_insights,
    "Reports": view_reports,
}


def _load_analytical_views() -> dict:
    """Load the shared SQL view bundle used by every analytics page."""
    try:
        return execute_analytical_views()
    except Exception as error:
        st.sidebar.warning(
            "Analytical data is currently unavailable. Run the data pipeline "
            f"before refreshing the dashboard. ({error})"
        )
        return {}


def _render_page(page: str, views: dict, filters) -> None:
    """Dispatch a selected page to its existing dashboard view function."""
    page_view = PAGE_VIEWS.get(page)
    if page_view is not None:
        page_view(views=views, filters=filters)


def main() -> None:
    st.set_page_config(
        page_title="Learning Behaviour & Course Completion Intelligence",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    initialize_session_state()

    render_header(
        title="🎓 Learning Behaviour & Course Completion Intelligence",
        subtitle="Predictive insights on student engagement, drop-off risk, and course completion."
    )

    st.sidebar.title("Navigation")
    st.sidebar.caption("Explore the learning analytics workspace")
    page = st.sidebar.radio(
        "Select page",
        [*NAVIGATION_PAGES, DATA_UPLOAD_PAGE],
        key=PAGE_KEY,
    )

    if page == DATA_UPLOAD_PAGE:
        view_dataset_upload()
        return

    raw_views = _load_analytical_views()
    filters = render_filter_sidebar(raw_views)
    filtered_views = filter_dashboard_views(raw_views, filters)
    _render_page(page, filtered_views, filters)


if __name__ == "__main__":
    main()

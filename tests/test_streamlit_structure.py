"""
Unit tests for Concept #41: Streamlit App Structure & Navigation.
"""

import pytest
from dashboard.app import NAVIGATION_PAGES, PAGE_VIEWS, main
from dashboard.views import (
    view_overview,
    view_student_behaviour,
    view_course_analytics,
    view_dropout_risk,
    view_behaviour_trends,
    view_sql_insights,
    view_reports
)


def test_streamlit_app_imports():
    """Verify app and views modules import without syntax or module errors."""
    assert callable(main)
    assert callable(view_overview)
    assert callable(view_student_behaviour)
    assert callable(view_course_analytics)
    assert callable(view_dropout_risk)
    assert callable(view_behaviour_trends)
    assert callable(view_sql_insights)
    assert callable(view_reports)


def test_views_exist_in_navigation():
    """Verify all 7 required navigation pages have corresponding view functions."""
    required_pages = [
        ("Overview", view_overview),
        ("Student Behaviour", view_student_behaviour),
        ("Course Analytics", view_course_analytics),
        ("Dropout Risk", view_dropout_risk),
        ("Behaviour Trends", view_behaviour_trends),
        ("SQL Insights", view_sql_insights),
        ("Reports", view_reports)
    ]
    for page_name, view_fn in required_pages:
        assert callable(view_fn), f"View handler for '{page_name}' must be a callable function"


def test_primary_navigation_registry_matches_required_pages():
    """Keep the primary navigation limited to the seven analytics pages."""
    expected_pages = (
        "Overview",
        "Student Behaviour",
        "Course Analytics",
        "Dropout Risk",
        "Behaviour Trends",
        "SQL Insights",
        "Reports",
    )
    assert NAVIGATION_PAGES == expected_pages
    assert set(PAGE_VIEWS) == set(expected_pages)

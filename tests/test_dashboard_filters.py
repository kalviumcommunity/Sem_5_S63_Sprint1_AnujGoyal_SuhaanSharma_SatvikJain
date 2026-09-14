"""Tests for shared Streamlit dashboard filter behavior."""

from datetime import date

import pandas as pd

from dashboard.filters import (
    DashboardFilters,
    calculate_filtered_kpis,
    filter_dashboard_views,
)


def sample_views():
    """Return learner-level analytical rows used by filter tests."""
    learners = pd.DataFrame({
        "student_id": ["S001", "S002", "S003"],
        "target_course_id": ["C101", "C101", "C202"],
        "course_title": ["Python", "Python", "SQL"],
        "registration_date": ["2026-01-05", "2026-02-10", "2026-02-12"],
        "completion_status": ["Completed", "Dropped", "In Progress"],
        "dropout_risk_level": ["Low", "Critical", "Moderate"],
        "engagement_score": [90.0, 25.0, 60.0],
        "quiz_average": [88.0, 35.0, 72.0],
        "avg_session_duration": [45.0, 15.0, 30.0],
        "course_progress": [100.0, 20.0, 55.0],
    })
    return {"student_engagement_view": learners}


def test_filter_dashboard_views_applies_shared_selections():
    filters = DashboardFilters(
        courses=["Python"],
        date_range=(date(2026, 1, 1), date(2026, 1, 31)),
        completion_statuses=["Completed"],
        risk_levels=["Low"],
        learner_segments=["High Engagement"],
        minimum_quiz_score=80.0,
    )

    filtered = filter_dashboard_views(sample_views(), filters)

    learners = filtered["student_engagement_view"]
    assert learners["student_id"].tolist() == ["S001"]
    assert filtered["course_performance_view"]["completion_rate_pct"].tolist() == [100.0]


def test_filtered_kpis_use_the_filtered_learner_view():
    filters = DashboardFilters(
        courses=["Python"],
        completion_statuses=["Completed", "Dropped"],
        risk_levels=["Low", "Critical"],
        learner_segments=["Low Engagement", "High Engagement"],
    )
    filtered = filter_dashboard_views(sample_views(), filters)

    kpis = calculate_filtered_kpis(filtered)

    assert kpis["total_students"] == 2
    assert kpis["completion_rate_pct"] == 50.0
    assert kpis["dropout_rate_pct"] == 50.0
    assert kpis["avg_quiz_score_pct"] == 61.5
    assert kpis["at_risk_learner_count"] == 1
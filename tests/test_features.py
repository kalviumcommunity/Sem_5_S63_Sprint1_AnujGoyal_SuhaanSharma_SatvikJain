"""
Unit tests for Concept #16: Feature Engineering & Derived Business Columns.
Tests behavioral derivations: average_session_duration, sessions_per_week, quiz_average,
quiz_attempt_count, course_progress, progress_velocity, days_since_last_activity,
completion_rate, learning_consistency, engagement_score, and formula documentation.
"""

import pytest
import pandas as pd
import numpy as np

from src.features import (
    engineer_behavioral_features,
    get_feature_dictionary,
    FEATURE_FORMULAS
)


@pytest.fixture
def sample_student_360():
    """Provides a realistic Student 360 DataFrame with active, moderate, and inactive learners."""
    return pd.DataFrame({
        "student_id": ["S001", "S002", "S003"],
        "registration_date": ["2026-01-01", "2026-01-15", "2026-02-01"],
        "target_course_id": ["C101", "C101", "C102"],
        "total_modules": [10, 10, 8],
        "total_quizzes": [4, 4, 2],
        "total_sessions": [8, 2, 0],
        "total_duration_minutes": [360.0, 60.0, 0.0],
        "total_active_minutes": [300.0, 45.0, 0.0],
        "total_idle_minutes": [60.0, 15.0, 0.0],
        "active_learning_ratio": [0.833, 0.75, 0.0],
        "last_session_date": ["2026-02-28", "2026-01-20", None],
        "total_quiz_attempts": [4, 1, 0],
        "quizzes_passed": [4, 1, 0],
        "quizzes_failed": [0, 0, 0],
        "avg_quiz_score": [88.5, 75.0, 0.0],
        "quiz_pass_rate": [100.0, 100.0, 0.0],
        "latest_quiz_date": ["2026-02-27", "2026-01-18", None],
        "progress_pct": [100.0, 25.0, 0.0],
        "completion_status": ["Completed", "In Progress", "Dropped"]
    })


def test_engineer_behavioral_features(sample_student_360):
    """Test full behavioral feature engineering calculations."""
    as_of = "2026-03-01"
    res = engineer_behavioral_features(sample_student_360, as_of_date=as_of)

    # 1. Average Session Duration
    assert res.at[0, "average_session_duration"] == 45.0  # 360 / 8 = 45.0m
    assert res.at[1, "average_session_duration"] == 30.0  # 60 / 2 = 30.0m
    assert res.at[2, "average_session_duration"] == 0.0   # 0 sessions

    # 2. Sessions Per Week
    assert res.at[0, "sessions_per_week"] > 0.5
    assert res.at[2, "sessions_per_week"] == 0.0

    # 3. Quiz Metrics
    assert res.at[0, "quiz_average"] == 88.5
    assert res.at[0, "quiz_attempt_count"] == 4
    assert res.at[2, "quiz_attempt_count"] == 0

    # 4. Course Progress & Progress Velocity
    assert res.at[0, "course_progress"] == 100.0
    assert res.at[0, "progress_velocity"] > 0.0

    # 5. Inactivity Recency (days_since_last_activity)
    # S001 active on 2026-02-28, as_of is 2026-03-01 -> 1 day
    assert res.at[0, "days_since_last_activity"] == 1
    # S002 active on 2026-01-20, as_of is 2026-03-01 -> 40 days
    assert res.at[1, "days_since_last_activity"] == 40

    # 6. Completion Rate Target Flag
    assert res.at[0, "completion_rate"] == 1.0
    assert res.at[1, "completion_rate"] == 0.0
    assert res.at[2, "completion_rate"] == 0.0

    # 7. Learning Consistency & Composite Engagement Score
    assert 0.0 <= res.at[0, "learning_consistency"] <= 1.0
    assert 0.0 <= res.at[0, "engagement_score"] <= 100.0
    assert res.at[0, "engagement_score"] > res.at[1, "engagement_score"]
    assert res.at[1, "engagement_score"] > res.at[2, "engagement_score"]


def test_get_feature_dictionary():
    """Test feature dictionary documentation generation."""
    f_df = get_feature_dictionary()

    assert isinstance(f_df, pd.DataFrame)
    assert len(f_df) == len(FEATURE_FORMULAS)
    assert "Feature Name" in f_df.columns
    assert "Mathematical Formula" in f_df.columns
    assert "engagement_score" in f_df["Feature Name"].values

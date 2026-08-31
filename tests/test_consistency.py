"""
Unit tests for Concept #14: Data Consistency & Validation Rules.
Tests business validation rules, score ranges, positive durations, approved statuses,
valid identifiers, logical date boundaries, registration-before-activity constraints, and audit reports.
"""

import pytest
import pandas as pd
import numpy as np

from src.consistency import (
    validate_entity_consistency,
    validate_all_consistency,
    generate_consistency_scorecard,
    ConsistencyReport,
    RuleViolation,
    APPROVED_COMPLETION_STATUSES
)


@pytest.fixture
def valid_students_df():
    """Provides a valid students DataFrame complying with all business rules."""
    return pd.DataFrame({
        "student_id": ["S001", "S002"],
        "registration_date": ["2026-01-01", "2026-01-02"],
        "age": [22, 28],
        "gender": ["Female", "Male"],
        "education_level": ["Undergraduate", "Postgraduate"],
        "device_type": ["Laptop", "Mobile"],
        "target_course_id": ["C101", "C102"],
        "completion_status": ["Completed", "In Progress"]
    })


@pytest.fixture
def invalid_students_df():
    """Provides a students DataFrame with status, age, and ID violations."""
    return pd.DataFrame({
        "student_id": ["S001", "NAN", "S003"],
        "registration_date": ["2026-01-01", "2026-01-02", "2026-01-03"],
        "age": [22, 5, 120],  # 5 and 120 are outside 15-90 range
        "completion_status": ["Completed", "GraduatedWithHonors", "Suspended"]  # Unapproved statuses
    })


@pytest.fixture
def invalid_sessions_df():
    """Provides sessions with negative duration and chronological inconsistency."""
    return pd.DataFrame({
        "session_id": ["SES01", "SES02", "SES03"],
        "student_id": ["S001", "S001", "S002"],
        "course_id": ["C101", "C101", "C101"],
        "session_start": ["2026-01-10 10:00:00", "2026-01-11 15:00:00", "2026-01-12 09:00:00"],
        "session_end": ["2026-01-10 10:45:00", "2026-01-11 14:00:00", "2026-01-12 09:30:00"],  # SES02 start > end!
        "duration_minutes": [45.0, -60.0, 0.0]  # SES02 and SES03 violate positive duration
    })


@pytest.fixture
def invalid_quizzes_df():
    """Provides quizzes with score boundary violations."""
    return pd.DataFrame({
        "quiz_attempt_id": ["QA01", "QA02", "QA03"],
        "student_id": ["S001", "S001", "S002"],
        "course_id": ["C101", "C101", "C101"],
        "quiz_id": ["QZ1", "QZ1", "QZ2"],
        "attempt_number": [1, 2, 1],
        "score_percentage": [85.0, 150.0, -10.0],  # 150 and -10 violate 0-100%
        "passed": [1, 1, 0]
    })


def test_validate_valid_students_dataset(valid_students_df):
    """Test that a fully compliant dataset achieves 100% pass rate."""
    _, report = validate_entity_consistency(valid_students_df, entity_name="students")

    assert isinstance(report, ConsistencyReport)
    assert report.pass_rate_pct == 100.0
    assert report.invalid_records == 0
    assert len(report.violations) == 0


def test_validate_student_rules_violations(invalid_students_df):
    """Test detection of unapproved statuses, invalid IDs, and extreme ages."""
    _, report = validate_entity_consistency(invalid_students_df, entity_name="students")

    assert report.invalid_records > 0
    assert len(report.violations) >= 3

    # Verify violations DataFrame structure
    v_df = report.to_violations_df()
    assert isinstance(v_df, pd.DataFrame)
    assert "Approved Completion Status" in v_df["Rule"].values
    assert "Valid Learner Age Range (15-90)" in v_df["Rule"].values


def test_validate_sessions_duration_and_timestamps(invalid_sessions_df):
    """Test detection of non-positive duration and inverted session timestamps."""
    _, report = validate_entity_consistency(invalid_sessions_df, entity_name="sessions")

    assert report.invalid_records > 0
    v_df = report.to_violations_df()

    assert "Positive Session Duration (> 0.0 mins)" in v_df["Rule"].values
    assert "Logical Session Timestamps (Start <= End)" in v_df["Rule"].values


def test_validate_quiz_score_boundaries(invalid_quizzes_df):
    """Test detection of out-of-bounds quiz scores (< 0% or > 100%)."""
    _, report = validate_entity_consistency(invalid_quizzes_df, entity_name="quizzes")

    assert report.invalid_records == 2
    v_df = report.to_violations_df()
    assert "Quiz Score Range (0.0 to 100.0%)" in v_df["Rule"].values


def test_validate_cross_entity_registration_before_activity(valid_students_df):
    """Test cross-entity check where session activity occurs before student enrollment date."""
    # Student S001 enrolled on 2026-01-01, session is on 2025-12-20 (prior to enrollment!)
    prior_session_df = pd.DataFrame({
        "session_id": ["SES_EARLY"],
        "student_id": ["S001"],
        "course_id": ["C101"],
        "session_start": ["2025-12-20 10:00:00"],
        "session_end": ["2025-12-20 11:00:00"],
        "duration_minutes": [60.0]
    })

    _, report = validate_entity_consistency(
        prior_session_df,
        entity_name="sessions",
        students_df=valid_students_df
    )

    assert len(report.violations) > 0
    v_df = report.to_violations_df()
    assert "Enrollment Prior to Activity Date" in v_df["Rule"].values


def test_generate_consistency_scorecard(invalid_students_df, invalid_sessions_df):
    """Test comparative consistency scorecard across multiple entities."""
    datasets = {
        "students": invalid_students_df,
        "sessions": invalid_sessions_df
    }
    _, reports = validate_all_consistency(datasets)
    scorecard = generate_consistency_scorecard(reports)

    assert isinstance(scorecard, pd.DataFrame)
    assert len(scorecard) > 0
    assert "Entity" in scorecard.columns
    assert "Business Rule" in scorecard.columns
    assert "Pass Rate %" in scorecard.columns

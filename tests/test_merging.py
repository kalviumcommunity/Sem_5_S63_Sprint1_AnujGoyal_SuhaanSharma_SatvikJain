"""
Unit tests for Concept #15: Multi-Source Merging & Join Validation.
Tests relational joins, granularity preservation, session/quiz aggregations,
expansion factor tracking, orphan diagnostics, and Student 360 analytical dataset generation.
"""

import pytest
import pandas as pd
import numpy as np

from src.merging import (
    validate_two_table_join,
    aggregate_student_sessions,
    aggregate_student_quizzes,
    build_student_360_dataset,
    JoinValidationSummary,
    JoinAuditReport
)


@pytest.fixture
def mock_students():
    return pd.DataFrame({
        "student_id": ["S001", "S002", "S003"],
        "registration_date": ["2026-01-01", "2026-01-02", "2026-01-03"],
        "age": [21, 24, 29],
        "target_course_id": ["C101", "C101", "C102"],
        "completion_status": ["Completed", "In Progress", "Dropped"]
    })


@pytest.fixture
def mock_courses():
    return pd.DataFrame({
        "course_id": ["C101", "C102"],
        "course_title": ["Python Data Science", "Cloud Architecture"],
        "category": ["Data Science", "Cloud Computing"],
        "total_modules": [10, 8],
        "total_quizzes": [4, 2]
    })


@pytest.fixture
def mock_sessions():
    return pd.DataFrame({
        "session_id": ["SES01", "SES02", "SES03", "SES_ORPHAN"],
        "student_id": ["S001", "S001", "S002", "S_UNKNOWN"],  # S_UNKNOWN is orphan
        "course_id": ["C101", "C101", "C101", "C101"],
        "session_start": ["2026-01-10 10:00:00", "2026-01-12 14:00:00", "2026-01-15 09:00:00", "2026-01-16 11:00:00"],
        "duration_minutes": [60.0, 40.0, 30.0, 45.0],
        "active_minutes": [50.0, 35.0, 25.0, 40.0],
        "idle_minutes": [10.0, 5.0, 5.0, 5.0]
    })


@pytest.fixture
def mock_quizzes():
    return pd.DataFrame({
        "quiz_attempt_id": ["QA01", "QA02", "QA03"],
        "student_id": ["S001", "S001", "S002"],
        "course_id": ["C101", "C101", "C101"],
        "quiz_id": ["QZ1", "QZ2", "QZ1"],
        "attempt_number": [1, 1, 1],
        "attempt_date": ["2026-01-11", "2026-01-14", "2026-01-16"],
        "score_percentage": [85.0, 90.0, 60.0],
        "passed": [1, 1, 0]
    })


def test_validate_two_table_join(mock_students, mock_courses):
    """Test two-table merge validation and diagnostics."""
    merged, summary = validate_two_table_join(
        left_df=mock_students,
        right_df=mock_courses,
        left_on="target_course_id",
        right_on="course_id",
        left_name="Students",
        right_name="Courses"
    )

    assert isinstance(summary, JoinValidationSummary)
    assert len(merged) == len(mock_students)
    assert summary.expansion_factor == 1.0
    assert summary.unmatched_left_rows == 0
    assert "course_title" in merged.columns


def test_aggregate_student_sessions(mock_sessions):
    """Test aggregation of session event telemetry."""
    agg = aggregate_student_sessions(mock_sessions)

    assert len(agg) == 3  # S001, S002, S_UNKNOWN
    s001 = agg[agg["student_id"] == "S001"].iloc[0]
    assert s001["total_sessions"] == 2
    assert s001["total_duration_minutes"] == 100.0
    assert s001["total_active_minutes"] == 85.0
    assert s001["active_learning_ratio"] == 0.85


def test_aggregate_student_quizzes(mock_quizzes):
    """Test aggregation of quiz attempt logs."""
    agg = aggregate_student_quizzes(mock_quizzes)

    assert len(agg) == 2  # S001, S002
    s001 = agg[agg["student_id"] == "S001"].iloc[0]
    assert s001["total_quiz_attempts"] == 2
    assert s001["quizzes_passed"] == 2
    assert s001["avg_quiz_score"] == 87.5
    assert s001["quiz_pass_rate"] == 100.0


def test_build_student_360_dataset(mock_students, mock_courses, mock_sessions, mock_quizzes):
    """Test full multi-source Student 360 dataset construction and join auditing."""
    s360_df, report = build_student_360_dataset(
        mock_students,
        mock_courses,
        mock_sessions,
        mock_quizzes
    )

    # 1. Granularity: exactly matches student count (3 rows)
    assert len(s360_df) == 3
    assert list(s360_df["student_id"]) == ["S001", "S002", "S003"]

    # 2. Key metrics populated
    s001 = s360_df[s360_df["student_id"] == "S001"].iloc[0]
    assert s001["total_sessions"] == 2
    assert s001["quizzes_passed"] == 2
    assert s001["progress_pct"] == 50.0  # 2 passed / 4 total quizzes = 50%

    # 3. Inactive student S003 defaulted cleanly
    s003 = s360_df[s360_df["student_id"] == "S003"].iloc[0]
    assert s003["total_sessions"] == 0
    assert s003["total_quiz_attempts"] == 0
    assert s003["progress_pct"] == 0.0

    # 4. Orphan diagnostics
    assert isinstance(report, JoinAuditReport)
    assert report.orphan_diagnostics["orphan_sessions_unregistered_students"] == 1  # S_UNKNOWN
    assert report.orphan_diagnostics["registered_students_zero_sessions"] == 1      # S003
    assert report.orphan_diagnostics["registered_students_zero_quizzes"] == 1       # S003
    assert report.orphan_diagnostics["granularity_preserved"] is True


def test_join_audit_report_summary(mock_students, mock_courses, mock_sessions, mock_quizzes):
    """Test conversion of JoinAuditReport into tabular summary DataFrame."""
    _, report = build_student_360_dataset(
        mock_students,
        mock_courses,
        mock_sessions,
        mock_quizzes
    )
    summary_df = report.to_summary_df()

    assert isinstance(summary_df, pd.DataFrame)
    assert len(summary_df) == 3  # 3 join steps
    assert "Left Table" in summary_df.columns
    assert "Right Table" in summary_df.columns
    assert "Expansion Factor" in summary_df.columns

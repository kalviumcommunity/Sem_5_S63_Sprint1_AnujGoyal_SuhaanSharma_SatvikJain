"""
Unit tests for Concept #10: Duplicate Detection & Record Deduplication.
Tests exact duplicate removal, business-key deduplication with tie-breaking,
audit reporting, scorecard generation, and pipeline integration.
"""

import pytest
import pandas as pd
import numpy as np

from src.deduplication import (
    detect_duplicates,
    deduplicate_dataset,
    deduplicate_all_datasets,
    generate_deduplication_scorecard,
    DeduplicationReport
)
from src.cleaning import clean_dataframe


@pytest.fixture
def duplicate_students_df():
    """Provides a students DataFrame with exact and business-key duplicate records."""
    return pd.DataFrame({
        "student_id": ["S001", "S001", "S001", "S002", "S003"],
        "registration_date": ["2026-01-01", "2026-01-01", "2026-01-05", "2026-01-02", "2026-01-03"],
        "age": [22, 22, 22, 25, 28],
        "gender": ["Female", "Female", None, "Male", "Female"],
        "education_level": ["Undergraduate", "Undergraduate", "Undergraduate", "Postgraduate", None],
        "device_type": ["Laptop", "Laptop", "Mobile", "Desktop", "Tablet"],
        "target_course_id": ["C101", "C101", "C101", "C102", "C101"],
        "completion_status": ["Completed", "Completed", "Completed", "In Progress", "Dropped"]
    })


@pytest.fixture
def duplicate_sessions_df():
    """Provides a sessions DataFrame with duplicate sessions."""
    return pd.DataFrame({
        "session_id": ["SES01", "SES01", "SES02", "SES03"],
        "student_id": ["S001", "S001", "S002", "S003"],
        "course_id": ["C101", "C101", "C101", "C102"],
        "session_start": ["2026-02-01 10:00:00", "2026-02-01 10:00:00", "2026-02-01 11:00:00", "2026-02-01 12:00:00"],
        "duration_minutes": [30.0, 60.0, 45.0, 20.0],  # SES01 row 2 has higher duration
        "active_minutes": [25.0, 50.0, 35.0, 15.0]
    })


@pytest.fixture
def duplicate_quizzes_df():
    """Provides a quizzes DataFrame with duplicate quiz attempts."""
    return pd.DataFrame({
        "quiz_attempt_id": ["QA01", "QA01", "QA02", "QA03"],
        "student_id": ["S001", "S001", "S002", "S003"],
        "course_id": ["C101", "C101", "C101", "C102"],
        "quiz_id": ["QZ1", "QZ1", "QZ1", "QZ2"],
        "attempt_number": [1, 1, 1, 1],
        "score_percentage": [60.0, 90.0, 80.0, 75.0],  # QA01 row 2 has higher score
        "passed": [0, 1, 1, 1]
    })


def test_detect_duplicates(duplicate_students_df):
    """Test duplicate detection statistics."""
    stats = detect_duplicates(duplicate_students_df, entity_name="students")

    assert stats["total_rows"] == 5
    assert stats["exact_duplicate_rows"] == 1  # Rows 0 and 1 are exact duplicates
    assert stats["business_key_duplicates"] == 2  # S001 appears 3 times total (2 duplicates)
    assert stats["business_keys_used"] == ["student_id"]


def test_deduplicate_students(duplicate_students_df):
    """Test students deduplication keeping the most complete non-null record."""
    deduped_df, report = deduplicate_dataset(duplicate_students_df, entity_name="students")

    assert len(deduped_df) == 3
    assert list(deduped_df["student_id"]) == ["S001", "S002", "S003"]
    assert report.total_duplicates_removed == 2
    assert report.exact_duplicates_removed == 1
    assert report.business_key_duplicates_removed == 1


def test_deduplicate_sessions_tie_breaking(duplicate_sessions_df):
    """Test sessions deduplication preserves the session with highest engagement."""
    deduped_df, report = deduplicate_dataset(duplicate_sessions_df, entity_name="sessions")

    assert len(deduped_df) == 3
    ses01 = deduped_df[deduped_df["session_id"] == "SES01"]
    assert len(ses01) == 1
    # Preserves duration 60.0 over 30.0
    assert ses01["duration_minutes"].iloc[0] == 60.0


def test_deduplicate_quizzes_tie_breaking(duplicate_quizzes_df):
    """Test quizzes deduplication preserves the highest validated score."""
    deduped_df, report = deduplicate_dataset(duplicate_quizzes_df, entity_name="quizzes")

    assert len(deduped_df) == 3
    qa01 = deduped_df[deduped_df["quiz_attempt_id"] == "QA01"]
    assert len(qa01) == 1
    assert qa01["score_percentage"].iloc[0] == 90.0
    assert qa01["passed"].iloc[0] == 1


def test_deduplication_report_summary(duplicate_students_df):
    """Test DeduplicationReport structure and summary DataFrame conversion."""
    _, report = deduplicate_dataset(duplicate_students_df, entity_name="students")

    assert isinstance(report, DeduplicationReport)
    assert report.initial_rows == 5
    assert report.final_rows == 3
    assert report.total_duplicates_removed == 2

    summary_df = report.to_summary_df()
    assert isinstance(summary_df, pd.DataFrame)
    assert summary_df["Total Duplicates Removed"].iloc[0] == 2


def test_generate_deduplication_scorecard(duplicate_students_df, duplicate_sessions_df):
    """Test multi-entity comparative scorecard generation."""
    datasets = {
        "students": duplicate_students_df,
        "sessions": duplicate_sessions_df
    }
    _, reports = deduplicate_all_datasets(datasets)
    scorecard = generate_deduplication_scorecard(reports)

    assert isinstance(scorecard, pd.DataFrame)
    assert len(scorecard) == 2
    assert "Entity" in scorecard.columns
    assert "Exact Duplicates" in scorecard.columns
    assert "Business Key Duplicates" in scorecard.columns


def test_clean_dataframe_deduplication_integration(duplicate_students_df):
    """Test clean_dataframe runs deduplication as stage 1."""
    cleaned = clean_dataframe(duplicate_students_df, entity_name="students")
    assert len(cleaned) == 3

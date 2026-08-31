"""
Unit tests for Concept #8: Missing Value Detection & Imputation.
Tests detection, domain-specific imputation rules, unrecoverable key drops, and audit reporting.
"""

import pytest
import numpy as np
import pandas as pd

from src.imputation import (
    detect_missing_values,
    impute_dataset,
    impute_all_datasets,
    ImputationReport
)
from src.cleaning import clean_dataframe


@pytest.fixture
def students_with_nulls():
    """Provides a students DataFrame with various missing values."""
    return pd.DataFrame({
        "student_id": ["S001", "S002", None, "S004"],
        "registration_date": ["2026-01-01", "2026-01-02", "2026-01-03", "2026-01-04"],
        "age": [20, np.nan, 30, 40],
        "gender": ["Female", None, "Male", None],
        "education_level": [None, "Undergraduate", "Postgraduate", None],
        "device_type": ["Laptop", None, "Mobile", "Desktop"],
        "target_course_id": ["C101", None, "C102", "C101"],
        "completion_status": ["Completed", None, "Dropped", None]
    })


@pytest.fixture
def sessions_with_nulls():
    """Provides a sessions DataFrame with missing duration metrics."""
    return pd.DataFrame({
        "session_id": ["SES01", "SES02", "SES03", None],
        "student_id": ["S001", "S002", "S003", "S004"],
        "course_id": ["C101", "C101", "C102", "C102"],
        "duration_minutes": [60.0, np.nan, 30.0, 45.0],
        "active_minutes": [50.0, 40.0, np.nan, 35.0],
        "idle_minutes": [10.0, 5.0, 5.0, np.nan]
    })


@pytest.fixture
def quizzes_with_nulls():
    """Provides a quizzes DataFrame with missing scores and attempts."""
    return pd.DataFrame({
        "quiz_attempt_id": ["QA01", "QA02", "QA03", None],
        "student_id": ["S001", "S002", "S003", "S004"],
        "course_id": ["C101", "C101", "C102", "C102"],
        "quiz_id": ["QZ1", "QZ1", "QZ2", "QZ2"],
        "attempt_number": [1, np.nan, 2, 1],
        "score_percentage": [80.0, np.nan, 60.0, 90.0],
        "time_taken_minutes": [15.0, np.nan, 20.0, 18.0],
        "passed": [1, np.nan, 0, 1]
    })


def test_detect_missing_values(students_with_nulls):
    """Test missing value detection across rows and columns."""
    report = detect_missing_values(students_with_nulls, dataset_name="Students")

    assert report["total_missing_cells"] > 0
    assert report["rows_with_missing"] == 4
    assert "age" in report["column_missing"]
    assert report["column_missing"]["age"]["missing_count"] == 1


def test_impute_students_rules(students_with_nulls):
    """Test domain-aware imputation on students entity."""
    cleaned_df, report = impute_dataset(students_with_nulls, entity_name="students")

    # 1. Row with null student_id must be dropped
    assert len(cleaned_df) == 3
    assert None not in cleaned_df["student_id"].values

    # 2. Age should use median (median of 20, 40 is 30) rather than 0
    assert cleaned_df["age"].isnull().sum() == 0
    assert (cleaned_df["age"] > 0).all()

    # 3. Categoricals filled with explicit 'Unknown'
    assert (cleaned_df["gender"].isin(["Female", "Male", "Unknown"])).all()
    assert (cleaned_df["education_level"].isin(["Undergraduate", "Postgraduate", "Unknown"])).all()
    assert (cleaned_df["device_type"].isin(["Laptop", "Mobile", "Desktop", "Unknown"])).all()

    # 4. Status filled with 'In Progress'
    assert "In Progress" in cleaned_df["completion_status"].values

    # 5. Report verification
    assert isinstance(report, ImputationReport)
    assert report.dropped_rows == 1
    assert report.final_missing_cells == 0
    assert report.final_completeness_pct == 100.0


def test_impute_sessions_rules(sessions_with_nulls):
    """Test duration and activity relationship imputation on sessions."""
    cleaned_df, report = impute_dataset(sessions_with_nulls, entity_name="sessions")

    # Null session_id dropped
    assert len(cleaned_df) == 3

    # Computed duration: 40 active + 5 idle = 45 duration for SES02
    assert cleaned_df.loc[cleaned_df["session_id"] == "SES02", "duration_minutes"].iloc[0] == 45.0

    # Active minutes computed from duration - idle for SES03: 30 - 5 = 25
    assert cleaned_df.loc[cleaned_df["session_id"] == "SES03", "active_minutes"].iloc[0] == 25.0

    assert cleaned_df["duration_minutes"].isnull().sum() == 0
    assert cleaned_df["active_minutes"].isnull().sum() == 0


def test_impute_quizzes_rules(quizzes_with_nulls):
    """Test quiz score median imputation and logical passed flag derivation."""
    cleaned_df, report = impute_dataset(quizzes_with_nulls, entity_name="quizzes")

    # Null quiz_attempt_id dropped
    assert len(cleaned_df) == 3

    # Score should NOT be 0; it should be median (e.g., 80 or 70)
    imputed_score = cleaned_df.loc[cleaned_df["quiz_attempt_id"] == "QA02", "score_percentage"].iloc[0]
    assert imputed_score >= 50.0

    # Attempt number defaulted to 1
    assert cleaned_df.loc[cleaned_df["quiz_attempt_id"] == "QA02", "attempt_number"].iloc[0] == 1

    # Passed flag recomputed from score >= 70
    assert cleaned_df.loc[cleaned_df["quiz_attempt_id"] == "QA02", "passed"].iloc[0] == 1


def test_imputation_report_dataframe_conversion(students_with_nulls):
    """Test generating a comparison DataFrame from ImputationReport."""
    _, report = impute_dataset(students_with_nulls, entity_name="students")
    comp_df = report.to_comparison_df()

    assert isinstance(comp_df, pd.DataFrame)
    assert len(comp_df) > 0
    assert "Column" in comp_df.columns
    assert "Strategy Applied" in comp_df.columns
    assert "Missing (Before)" in comp_df.columns


def test_clean_dataframe_integration(students_with_nulls):
    """Test clean_dataframe wrapper integrates imputation seamlessly."""
    cleaned = clean_dataframe(students_with_nulls, entity_name="students")
    assert len(cleaned) == 3
    assert cleaned["age"].isnull().sum() == 0

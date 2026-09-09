"""
Unit tests for Concept #34: SQL-Based Insight Validation.
"""

import sqlite3
import pytest
import pandas as pd
from pathlib import Path
from src.database import (
    init_database,
    load_processed_data_to_sqlite,
    validate_sql_insights_against_pandas,
)
from src.analysis import run_sql_insight_validation


@pytest.fixture
def populated_validation_db(tmp_path):
    """Fixture creating and populating a temporary SQLite database for insight validation testing."""
    db_file = tmp_path / "test_insight_validation.db"
    init_database(db_path=db_file)

    students_df = pd.DataFrame({
        "student_id": [f"S00{i}" for i in range(1, 11)],
        "registration_date": ["2026-01-05"] * 10,
        "age": [20, 21, 23, 24, 25, 29, 31, 35, 19, 28],
        "gender": ["Female"] * 5 + ["Male"] * 5,
        "education_level": ["Undergraduate"] * 5 + ["Postgraduate"] * 5,
        "device_type": ["Laptop"] * 4 + ["Desktop"] * 3 + ["Mobile"] * 3,
        "target_course_id": ["C001"] * 5 + ["C002"] * 5,
        "completion_status": ["Completed"] * 6 + ["In Progress"] * 2 + ["Dropped"] * 2
    })

    courses_df = pd.DataFrame({
        "course_id": ["C001", "C002"],
        "course_title": ["Python for Data Science", "SQL Database Analytics"],
        "category": ["Data Science", "Database"],
        "total_modules": [10, 8],
        "total_quizzes": [5, 4],
        "estimated_duration_hours": [20.0, 15.0]
    })

    sessions_df = pd.DataFrame({
        "session_id": [f"SES00{i}" for i in range(1, 9)],
        "student_id": [f"S00{i}" for i in range(1, 9)],
        "course_id": ["C001"] * 4 + ["C002"] * 4,
        "session_start": ["2026-02-01 10:00:00"] * 8,
        "session_end": ["2026-02-01 11:00:00"] * 8,
        "duration_minutes": [30.0, 45.0, 60.0, 20.0, 50.0, 35.0, 40.0, 55.0],
        "active_minutes": [25.0, 40.0, 50.0, 15.0, 40.0, 30.0, 35.0, 45.0],
        "idle_minutes": [5.0, 5.0, 10.0, 5.0, 10.0, 5.0, 5.0, 10.0]
    })

    quizzes_df = pd.DataFrame({
        "quiz_attempt_id": [f"QA00{i}" for i in range(1, 6)],
        "student_id": [f"S00{i}" for i in range(1, 6)],
        "course_id": ["C001"] * 5,
        "quiz_id": ["Q1"] * 5,
        "attempt_number": [1] * 5,
        "attempt_date": ["2026-02-05"] * 5,
        "score_percentage": [85.0, 90.0, 75.0, 60.0, 95.0],
        "time_taken_minutes": [20.0] * 5,
        "passed": [1, 1, 1, 0, 1]
    })

    behavioural_features_df = pd.DataFrame({
        "student_id": [f"S00{i}" for i in range(1, 11)],
        "engagement_score": [85.0, 90.0, 75.0, 45.0, 92.0, 78.0, 68.0, 50.0, 82.0, 88.0],
        "dropout_risk_level": ["Low", "Low", "Low", "Critical", "Low", "Low", "Moderate", "High", "Low", "Low"]
    })

    load_processed_data_to_sqlite({
        "students": students_df,
        "courses": courses_df,
        "sessions": sessions_df,
        "quizzes": quizzes_df,
        "behavioural_features": behavioural_features_df
    }, db_path=db_file)

    return db_file


def test_validate_sql_insights_against_pandas(populated_validation_db):
    """Verify that SQL business metrics match Pandas calculations."""
    report = validate_sql_insights_against_pandas(db_path=populated_validation_db)
    assert isinstance(report, dict)
    assert report["status"] == "VALID"
    assert len(report["discrepancies"]) == 0
    assert report["metrics_compared"] == 7

    comp = report["comparison_results"]
    assert comp["total_students"]["match"] is True
    assert comp["completion_rate_pct"]["sql_value"] == 60.0
    assert comp["completion_rate_pct"]["pandas_value"] == 60.0
    assert comp["dropout_rate_pct"]["sql_value"] == 20.0
    assert comp["dropout_rate_pct"]["pandas_value"] == 20.0
    assert comp["active_learner_count"]["sql_value"] == 8
    assert comp["at_risk_learner_count"]["sql_value"] == 2


def test_run_sql_insight_validation_wrapper(populated_validation_db):
    """Verify src.analysis wrapper runs validation cleanly."""
    res = run_sql_insight_validation(db_path=populated_validation_db)
    assert isinstance(res, dict)
    assert res["status"] == "VALID"


def test_validation_discrepancy_detection(populated_validation_db):
    """Verify validation engine correctly flags metric discrepancies when data differs."""
    mismatched_datasets = {
        "students": pd.DataFrame({
            "student_id": ["S001"],
            "completion_status": ["Dropped"]  # Forces 100% dropout in Pandas while SQL has 20%
        })
    }
    report = validate_sql_insights_against_pandas(db_path=populated_validation_db, datasets=mismatched_datasets)
    assert report["status"] == "INVALID"
    assert len(report["discrepancies"]) > 0

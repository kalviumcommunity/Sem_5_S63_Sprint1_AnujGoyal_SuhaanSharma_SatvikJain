"""
Unit tests for Concept #33: SQL Views & Aggregation Layer Design.
"""

import sqlite3
import pytest
import pandas as pd
from pathlib import Path
from src.database import (
    init_database,
    init_views,
    load_processed_data_to_sqlite,
    execute_analytical_views,
    validate_views_against_pandas,
    query_to_dataframe,
)
from src.utils import SQL_DIR


@pytest.fixture
def populated_views_db(tmp_path):
    """Fixture creating and populating a temporary SQLite database for views testing."""
    db_file = tmp_path / "test_views.db"
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
        "estimated_duration_hours": [20.0, 15.0],
        "difficulty_level": ["Intermediate", "Beginner"]
    })

    sessions_df = pd.DataFrame({
        "session_id": [f"SES00{i}" for i in range(1, 11)],
        "student_id": [f"S00{i}" for i in range(1, 11)],
        "course_id": ["C001"] * 5 + ["C002"] * 5,
        "session_start": ["2026-02-01 10:00:00"] * 10,
        "session_end": ["2026-02-01 11:00:00"] * 10,
        "duration_minutes": [30.0, 45.0, 60.0, 20.0, 50.0, 35.0, 40.0, 55.0, 25.0, 65.0],
        "active_minutes": [25.0, 40.0, 50.0, 15.0, 40.0, 30.0, 35.0, 45.0, 20.0, 55.0],
        "idle_minutes": [5.0, 5.0, 10.0, 5.0, 10.0, 5.0, 5.0, 10.0, 5.0, 10.0]
    })

    quizzes_df = pd.DataFrame({
        "quiz_attempt_id": [f"QA00{i}" for i in range(1, 11)],
        "student_id": [f"S00{i}" for i in range(1, 11)],
        "course_id": ["C001"] * 5 + ["C002"] * 5,
        "quiz_id": ["Q1"] * 10,
        "attempt_number": [1] * 10,
        "attempt_date": ["2026-02-05"] * 10,
        "score_percentage": [85.0, 90.0, 75.0, 60.0, 95.0, 80.0, 70.0, 65.0, 88.0, 92.0],
        "time_taken_minutes": [20.0] * 10,
        "passed": [1, 1, 1, 0, 1, 1, 1, 0, 1, 1]
    })

    behavioural_features_df = pd.DataFrame({
        "student_id": [f"S00{i}" for i in range(1, 11)],
        "engagement_score": [85.0, 90.0, 75.0, 45.0, 92.0, 78.0, 68.0, 50.0, 82.0, 88.0],
        "course_progress": [100.0, 100.0, 100.0, 40.0, 100.0, 100.0, 80.0, 30.0, 100.0, 100.0],
        "average_session_duration": [30.0, 45.0, 60.0, 20.0, 50.0, 35.0, 40.0, 55.0, 25.0, 65.0],
        "quiz_average": [85.0, 90.0, 75.0, 60.0, 95.0, 80.0, 70.0, 65.0, 88.0, 92.0],
        "days_since_last_activity": [2, 3, 1, 20, 4, 5, 8, 18, 1, 2],
        "sessions_per_week": [3.0, 4.0, 5.0, 1.0, 4.5, 3.5, 3.0, 2.0, 4.0, 5.0],
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


def test_views_creation_in_sqlite(populated_views_db):
    """Verify that all 4 views exist in SQLite schema."""
    conn = sqlite3.connect(str(populated_views_db))
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='view';")
    views = set(row[0] for row in cursor.fetchall())
    conn.close()

    assert "student_engagement_view" in views
    assert "course_performance_view" in views
    assert "dropout_risk_view" in views
    assert "weekly_activity_view" in views


def test_execute_analytical_views(populated_views_db):
    """Verify executing analytical views returns populated DataFrames."""
    views_dict = execute_analytical_views(db_path=populated_views_db)
    assert isinstance(views_dict, dict)
    assert len(views_dict) == 4

    se_df = views_dict["student_engagement_view"]
    assert not se_df.empty
    assert "course_title" in se_df.columns
    assert len(se_df) == 10

    cp_df = views_dict["course_performance_view"]
    assert not cp_df.empty
    assert "completion_rate_pct" in cp_df.columns
    assert len(cp_df) == 2

    dr_df = views_dict["dropout_risk_view"]
    assert not dr_df.empty
    assert "is_at_risk" in dr_df.columns
    assert dr_df["is_at_risk"].sum() == 2  # QA004 (Critical) and QA008 (High)

    wa_df = views_dict["weekly_activity_view"]
    assert not wa_df.empty
    assert "total_sessions" in wa_df.columns
    assert wa_df["total_sessions"].sum() == 10


def test_validate_views_against_pandas(populated_views_db):
    """Verify view results match Pandas calculations."""
    report = validate_views_against_pandas(db_path=populated_views_db)
    assert isinstance(report, dict)
    assert report["status"] == "VALID"
    assert len(report["errors"]) == 0
    assert report["validation_details"]["student_engagement_view"]["match"] is True
    assert report["validation_details"]["course_performance_view"]["match"] is True
    assert report["validation_details"]["dropout_risk_view"]["match"] is True
    assert report["validation_details"]["weekly_activity_view"]["match"] is True

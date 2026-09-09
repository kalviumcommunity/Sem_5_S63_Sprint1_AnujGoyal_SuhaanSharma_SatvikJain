"""
Unit tests for Concept #29: SQL Filtering, Grouping & Aggregation.
"""

import sqlite3
import pytest
import pandas as pd
from pathlib import Path
from src.database import (
    init_database,
    load_processed_data_to_sqlite,
    load_sql_queries_from_file,
    execute_aggregation_queries,
)
from src.analysis import run_aggregation_analysis
from src.utils import SQL_DIR


@pytest.fixture
def populated_aggregation_db(tmp_path):
    """Fixture creating and populating a temporary SQLite database for aggregation testing."""
    db_file = tmp_path / "test_aggregation.db"
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


def test_load_aggregation_queries_file():
    """Verify loading SQL queries from sql/aggregation.sql."""
    target_sql = SQL_DIR / "aggregation.sql"
    assert target_sql.exists()

    queries = load_sql_queries_from_file(target_sql)
    assert len(queries) >= 5
    assert "course_performance_analysis" in queries
    assert "learner_segment_analysis" in queries
    assert "high_inactivity_risk_analysis" in queries
    assert "age_demographic_engagement" in queries
    assert "quiz_performance_aggregation" in queries


def test_execute_aggregation_queries(populated_aggregation_db):
    """Verify executing filtering, grouping, and aggregation queries."""
    results = execute_aggregation_queries(db_path=populated_aggregation_db)
    assert isinstance(results, dict)
    assert "course_performance_analysis" in results

    course_df = results["course_performance_analysis"]
    assert not course_df.empty
    assert "completion_rate_pct" in course_df.columns
    assert "total_enrolled" in course_df.columns

    segment_df = results["learner_segment_analysis"]
    assert not segment_df.empty
    assert "avg_quiz_score" in segment_df.columns

    age_df = results["age_demographic_engagement"]
    assert not age_df.empty
    assert "age_group" in age_df.columns


def test_run_aggregation_analysis_wrapper(populated_aggregation_db):
    """Verify src.analysis wrapper runs aggregation analysis clean."""
    res = run_aggregation_analysis(db_path=populated_aggregation_db)
    assert isinstance(res, dict)
    assert "quiz_performance_aggregation" in res
    assert isinstance(res["quiz_performance_aggregation"], pd.DataFrame)

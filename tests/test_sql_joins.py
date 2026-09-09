"""
Unit tests for Concept #30: SQL Joins & Multi-Table Analysis.
"""

import sqlite3
import pytest
import pandas as pd
from pathlib import Path
from src.database import (
    init_database,
    load_processed_data_to_sqlite,
    load_sql_queries_from_file,
    execute_multi_table_joins,
    validate_join_expansion_integrity,
)
from src.analysis import run_multi_table_join_analysis
from src.utils import SQL_DIR


@pytest.fixture
def populated_joins_db(tmp_path):
    """Fixture creating and populating a multi-entity SQLite database for join testing."""
    db_file = tmp_path / "test_joins.db"
    init_database(db_path=db_file)

    students_df = pd.DataFrame({
        "student_id": [f"S00{i}" for i in range(1, 6)],
        "registration_date": ["2026-01-01"] * 5,
        "age": [20, 22, 25, 28, 30],
        "gender": ["Female", "Male", "Female", "Male", "Other"],
        "education_level": ["Undergraduate"] * 5,
        "device_type": ["Laptop"] * 5,
        "target_course_id": ["C001", "C001", "C002", "C002", "C001"],
        "completion_status": ["Completed", "Completed", "In Progress", "Dropped", "In Progress"]
    })

    courses_df = pd.DataFrame({
        "course_id": ["C001", "C002"],
        "course_title": ["Python for Data Science", "SQL Analytics"],
        "category": ["Data Science", "Database"],
        "total_modules": [10, 8],
        "total_quizzes": [5, 4],
        "estimated_duration_hours": [20.0, 15.0]
    })

    sessions_df = pd.DataFrame({
        "session_id": [f"SES00{i}" for i in range(1, 9)],
        "student_id": ["S001", "S001", "S002", "S003", "S003", "S004", "S005", "S005"],
        "course_id": ["C001", "C001", "C001", "C002", "C002", "C002", "C001", "C001"],
        "session_start": ["2026-02-01 10:00:00"] * 8,
        "session_end": ["2026-02-01 11:00:00"] * 8,
        "duration_minutes": [45.0, 30.0, 60.0, 25.0, 35.0, 20.0, 50.0, 40.0],
        "active_minutes": [35.0, 25.0, 50.0, 20.0, 30.0, 15.0, 40.0, 35.0],
        "idle_minutes": [10.0, 5.0, 10.0, 5.0, 5.0, 5.0, 10.0, 5.0]
    })

    quizzes_df = pd.DataFrame({
        "quiz_attempt_id": [f"QA00{i}" for i in range(1, 6)],
        "student_id": ["S001", "S002", "S003", "S004", "S005"],
        "course_id": ["C001", "C001", "C002", "C002", "C001"],
        "quiz_id": ["Q1"] * 5,
        "attempt_number": [1] * 5,
        "attempt_date": ["2026-02-05"] * 5,
        "score_percentage": [90.0, 85.0, 75.0, 40.0, 80.0],
        "time_taken_minutes": [20.0] * 5,
        "passed": [1, 1, 1, 0, 1]
    })

    behavioural_features_df = pd.DataFrame({
        "student_id": [f"S00{i}" for i in range(1, 6)],
        "average_session_duration": [37.5, 60.0, 30.0, 20.0, 45.0],
        "sessions_per_week": [4.0, 3.0, 2.5, 1.0, 3.5],
        "quiz_average": [90.0, 85.0, 75.0, 40.0, 80.0],
        "quiz_attempt_count": [1, 1, 1, 1, 1],
        "course_progress": [100.0, 100.0, 60.0, 20.0, 50.0],
        "progress_velocity": [10.0, 10.0, 5.0, 2.0, 4.0],
        "days_since_last_activity": [1, 2, 5, 25, 3],
        "learning_consistency": [0.85, 0.90, 0.70, 0.30, 0.75],
        "engagement_score": [92.0, 88.0, 65.0, 28.0, 72.0],
        "completion_rate": [1.0, 1.0, 0.0, 0.0, 0.0],
        "dropout_risk_level": ["Low", "Low", "Low", "Critical", "Low"]
    })

    load_processed_data_to_sqlite({
        "students": students_df,
        "courses": courses_df,
        "sessions": sessions_df,
        "quizzes": quizzes_df,
        "behavioural_features": behavioural_features_df
    }, db_path=db_file)

    return db_file


def test_load_multi_table_joins_file():
    """Verify parsing SQL queries from sql/multi_table_joins.sql."""
    target_sql = SQL_DIR / "multi_table_joins.sql"
    assert target_sql.exists()

    queries = load_sql_queries_from_file(target_sql)
    assert len(queries) >= 5
    assert "student_360_multi_table" in queries
    assert "course_completion_telemetry" in queries
    assert "high_risk_learner_diagnostics" in queries
    assert "quiz_session_correlation_join" in queries
    assert "join_duplication_validation" in queries


def test_execute_multi_table_joins(populated_joins_db):
    """Verify executing multi-table INNER and LEFT JOIN queries."""
    results = execute_multi_table_joins(db_path=populated_joins_db)
    assert isinstance(results, dict)

    s360_df = results["student_360_multi_table"]
    assert not s360_df.empty
    assert len(s360_df) == 5  # Preserves 5 students
    assert "course_title" in s360_df.columns
    assert "engagement_score" in s360_df.columns
    assert "total_sessions" in s360_df.columns

    telemetry_df = results["course_completion_telemetry"]
    assert not telemetry_df.empty

    high_risk_df = results["high_risk_learner_diagnostics"]
    assert not high_risk_df.empty
    assert len(high_risk_df) == 1  # 1 Critical risk student (S004)
    assert high_risk_df.iloc[0]["student_id"] == "S004"


def test_validate_join_expansion_integrity(populated_joins_db):
    """Verify non-duplication join expansion factor calculation."""
    report = validate_join_expansion_integrity(db_path=populated_joins_db)
    assert report["base_students_count"] == 5
    assert report["joined_records_count"] == 5
    assert report["expansion_factor"] == 1.0
    assert report["join_integrity_status"] == "VALID_NO_DUPLICATES"


def test_run_multi_table_join_analysis_wrapper(populated_joins_db):
    """Verify src.analysis wrapper runs multi-table join analysis."""
    results = run_multi_table_join_analysis(db_path=populated_joins_db)
    assert isinstance(results, dict)
    assert "student_360_multi_table" in results
    assert isinstance(results["student_360_multi_table"], pd.DataFrame)

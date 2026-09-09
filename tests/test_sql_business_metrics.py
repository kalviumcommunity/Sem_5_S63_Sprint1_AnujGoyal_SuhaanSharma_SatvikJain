"""
Unit tests for Concept #28: SQL Business Metrics Query Design.
"""

import sqlite3
import pytest
import pandas as pd
from pathlib import Path
from src.database import (
    init_database,
    load_processed_data_to_sqlite,
    load_sql_queries_from_file,
    execute_business_metrics,
)
from src.analysis import get_business_kpis


@pytest.fixture
def populated_db(tmp_path):
    """Fixture creating and populating a temporary SQLite database with known metrics."""
    db_file = tmp_path / "test_business_metrics.db"
    init_database(db_path=db_file)

    students_df = pd.DataFrame({
        "student_id": [f"S00{i}" for i in range(1, 11)],
        "registration_date": ["2026-01-01"] * 10,
        "age": [20 + i for i in range(10)],
        "gender": ["Female"] * 5 + ["Male"] * 5,
        "education_level": ["Undergraduate"] * 10,
        "device_type": ["Laptop"] * 10,
        "target_course_id": ["C001"] * 5 + ["C002"] * 5,
        "completion_status": ["Completed"] * 5 + ["In Progress"] * 3 + ["Dropped"] * 2
    })

    courses_df = pd.DataFrame({
        "course_id": ["C001", "C002"],
        "course_title": ["Python", "SQL"],
        "category": ["Data Science", "Database"],
        "total_modules": [10, 8],
        "total_quizzes": [5, 4],
        "estimated_duration_hours": [20.0, 15.0]
    })

    sessions_df = pd.DataFrame({
        "session_id": [f"SES00{i}" for i in range(1, 9)],
        "student_id": ["S001", "S002", "S003", "S004", "S005", "S006", "S007", "S008"],
        "course_id": ["C001"] * 4 + ["C002"] * 4,
        "session_start": ["2026-02-01 10:00:00"] * 8,
        "session_end": ["2026-02-01 10:30:00"] * 8,
        "duration_minutes": [30.0, 40.0, 50.0, 20.0, 60.0, 30.0, 45.0, 25.0],  # Mean: 37.5
        "active_minutes": [25.0, 35.0, 40.0, 15.0, 50.0, 25.0, 40.0, 20.0],
        "idle_minutes": [5.0, 5.0, 10.0, 5.0, 10.0, 5.0, 5.0, 5.0]
    })

    quizzes_df = pd.DataFrame({
        "quiz_attempt_id": [f"QA00{i}" for i in range(1, 6)],
        "student_id": ["S001", "S002", "S003", "S004", "S005"],
        "course_id": ["C001"] * 5,
        "quiz_id": ["Q1"] * 5,
        "attempt_number": [1] * 5,
        "attempt_date": ["2026-02-05"] * 5,
        "score_percentage": [80.0, 90.0, 70.0, 85.0, 95.0],  # Mean: 84.0
        "time_taken_minutes": [15.0] * 5,
        "passed": [1] * 5
    })

    behavioural_features_df = pd.DataFrame({
        "student_id": [f"S00{i}" for i in range(1, 11)],
        "dropout_risk_level": ["Low", "Low", "Low", "Low", "Low", "Medium", "High", "High", "Critical", "Critical"],
        "quiz_average": [80.0, 90.0, 70.0, 85.0, 95.0, 60.0, 50.0, 45.0, 30.0, 20.0],
        "average_session_duration": [30.0, 40.0, 50.0, 20.0, 60.0, 30.0, 45.0, 25.0, 15.0, 10.0]
    })

    load_processed_data_to_sqlite({
        "students": students_df,
        "courses": courses_df,
        "sessions": sessions_df,
        "quizzes": quizzes_df,
        "behavioural_features": behavioural_features_df
    }, db_path=db_file)

    return db_file


def test_load_sql_queries_from_file():
    """Verify parsing named queries from sql/business_metrics.sql."""
    queries = load_sql_queries_from_file()
    assert len(queries) >= 6
    assert "completion_rate" in queries
    assert "dropout_rate" in queries
    assert "average_quiz_score" in queries
    assert "average_session_duration" in queries
    assert "active_learner_count" in queries
    assert "at_risk_learner_count" in queries


def test_execute_business_metrics_kpi_values(populated_db):
    """Verify calculated KPI values match expected mathematical results."""
    results = execute_business_metrics(db_path=populated_db)
    kpis = results["kpis"]

    assert kpis["total_students"] == 10
    assert kpis["completion_rate_pct"] == 50.0  # 5/10 completed
    assert kpis["dropout_rate_pct"] == 20.0     # 2/10 dropped
    assert kpis["avg_quiz_score_pct"] == 84.0   # (80+90+70+85+95)/5 = 84.0
    assert kpis["avg_session_duration_minutes"] == 37.5  # Mean of [30,40,50,20,60,30,45,25]
    assert kpis["active_learner_count"] == 8    # 8 distinct students in sessions
    assert kpis["at_risk_learner_count"] == 4   # 2 High + 2 Critical


def test_get_business_kpis(populated_db):
    """Verify src.analysis wrapper retrieves KPI dictionary cleanly."""
    kpis = get_business_kpis(db_path=populated_db)
    assert isinstance(kpis, dict)
    assert kpis.get("completion_rate_pct") == 50.0
    assert kpis.get("at_risk_learner_count") == 4

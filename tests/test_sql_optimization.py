"""
Unit tests for Concept #32: Analytical SQL Query Optimisation.
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
    execute_aggregation_queries,
    execute_window_function_queries,
    create_database_indexes,
    explain_query_plan,
    benchmark_query,
)
from src.utils import SQL_DIR


@pytest.fixture
def populated_opt_db(tmp_path):
    """Fixture creating and populating a temporary SQLite database for optimization testing."""
    db_file = tmp_path / "test_optimization.db"
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


def test_index_creation(populated_opt_db):
    """Verify that performance indexes exist in the database."""
    created = create_database_indexes(db_path=populated_opt_db)
    assert len(created) >= 8

    conn = sqlite3.connect(str(populated_opt_db))
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index';")
    indexes = set(row[0] for row in cursor.fetchall())
    conn.close()

    assert "idx_students_target_course" in indexes
    assert "idx_sessions_student_start" in indexes
    assert "idx_quizzes_student_quiz" in indexes
    assert "idx_behavioural_risk" in indexes


def test_explain_query_plan_utility(populated_opt_db):
    """Verify EXPLAIN QUERY PLAN functionality."""
    query = "SELECT * FROM sessions WHERE student_id = 'S001' ORDER BY session_start;"
    df = explain_query_plan(query, db_path=populated_opt_db)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "detail" in df.columns


def test_benchmark_query_utility(populated_opt_db):
    """Verify benchmark_query timing metric measurement."""
    query = "SELECT COUNT(*) FROM students;"
    res = benchmark_query(query, db_path=populated_opt_db, runs=5)
    assert isinstance(res, dict)
    assert res["runs"] == 5
    assert "avg_time_ms" in res
    assert res["avg_time_ms"] >= 0.0


def test_optimized_query_execution_parity(populated_opt_db):
    """Verify all optimized SQL queries execute cleanly and produce valid outputs."""
    bm_res = execute_business_metrics(db_path=populated_opt_db)
    assert bm_res["kpis"]["total_students"] == 10
    assert bm_res["kpis"]["completion_rate_pct"] == 60.0
    assert bm_res["kpis"]["dropout_rate_pct"] == 20.0

    agg_res = execute_aggregation_queries(db_path=populated_opt_db)
    assert "course_performance_analysis" in agg_res
    assert not agg_res["course_performance_analysis"].empty

    wf_res = execute_window_function_queries(db_path=populated_opt_db)
    assert "course_learner_rankings" in wf_res
    assert not wf_res["course_learner_rankings"].empty

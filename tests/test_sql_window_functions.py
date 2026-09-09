"""
Unit tests for Concept #31: SQL Window Functions & Ranking Systems.
"""

import sqlite3
import pytest
import pandas as pd
from pathlib import Path
from src.database import (
    init_database,
    load_processed_data_to_sqlite,
    load_sql_queries_from_file,
    execute_window_function_queries,
)
from src.analysis import run_window_function_analysis
from src.utils import SQL_DIR


@pytest.fixture
def populated_window_db(tmp_path):
    """Fixture creating and populating a temporary SQLite database for window function testing."""
    db_file = tmp_path / "test_window_functions.db"
    init_database(db_path=db_file)

    students_df = pd.DataFrame({
        "student_id": ["S001", "S002", "S003", "S004"],
        "registration_date": ["2026-01-01"] * 4,
        "age": [22, 25, 28, 30],
        "gender": ["Female", "Male", "Female", "Male"],
        "education_level": ["Undergraduate"] * 4,
        "device_type": ["Laptop"] * 4,
        "target_course_id": ["C001", "C001", "C002", "C002"],
        "completion_status": ["Completed", "In Progress", "Completed", "Dropped"]
    })

    courses_df = pd.DataFrame({
        "course_id": ["C001", "C002"],
        "course_title": ["Python for Data Science", "SQL Analytics"],
        "category": ["Data Science", "Database"],
        "total_modules": [10, 8],
        "total_quizzes": [5, 4],
        "estimated_duration_hours": [20.0, 15.0]
    })

    # Sequential sessions for student S001 to test LAG and rolling average
    sessions_df = pd.DataFrame({
        "session_id": ["SES01", "SES02", "SES03", "SES04", "SES05", "SES06"],
        "student_id": ["S001", "S001", "S001", "S002", "S002", "S003"],
        "course_id": ["C001", "C001", "C001", "C001", "C001", "C002"],
        "session_start": [
            "2026-02-01 10:00:00", "2026-02-02 10:00:00", "2026-02-03 10:00:00",
            "2026-02-01 11:00:00", "2026-02-02 11:00:00", "2026-02-01 12:00:00"
        ],
        "session_end": [
            "2026-02-01 10:30:00", "2026-02-02 10:45:00", "2026-02-03 11:00:00",
            "2026-02-01 11:40:00", "2026-02-02 11:50:00", "2026-02-01 13:00:00"
        ],
        "duration_minutes": [30.0, 45.0, 60.0, 40.0, 50.0, 60.0],  # S001: 30, 45, 60
        "active_minutes": [25.0, 40.0, 50.0, 30.0, 40.0, 50.0],
        "idle_minutes": [5.0, 5.0, 10.0, 10.0, 10.0, 10.0]
    })

    # Multiple quiz attempts for S001 to test LAG and LEAD
    quizzes_df = pd.DataFrame({
        "quiz_attempt_id": ["QA01", "QA02", "QA03", "QA04"],
        "student_id": ["S001", "S001", "S001", "S002"],
        "course_id": ["C001", "C001", "C001", "C001"],
        "quiz_id": ["Q1", "Q1", "Q1", "Q1"],
        "attempt_number": [1, 2, 3, 1],
        "attempt_date": ["2026-02-01", "2026-02-03", "2026-02-05", "2026-02-01"],
        "score_percentage": [60.0, 75.0, 90.0, 80.0],
        "time_taken_minutes": [20.0, 18.0, 15.0, 20.0],
        "passed": [0, 1, 1, 1]
    })

    behavioural_features_df = pd.DataFrame({
        "student_id": ["S001", "S002", "S003", "S004"],
        "engagement_score": [90.0, 70.0, 85.0, 30.0],
        "quiz_average": [75.0, 80.0, 85.0, 40.0],
        "average_session_duration": [45.0, 45.0, 60.0, 20.0],
        "sessions_per_week": [3.0, 2.0, 2.5, 0.5],
        "days_since_last_activity": [1, 3, 2, 20],
        "dropout_risk_level": ["Low", "Low", "Low", "Critical"]
    })

    load_processed_data_to_sqlite({
        "students": students_df,
        "courses": courses_df,
        "sessions": sessions_df,
        "quizzes": quizzes_df,
        "behavioural_features": behavioural_features_df
    }, db_path=db_file)

    return db_file


def test_load_window_function_queries_file():
    """Verify parsing SQL queries from sql/window_functions.sql."""
    target_sql = SQL_DIR / "window_functions.sql"
    assert target_sql.exists()

    queries = load_sql_queries_from_file(target_sql)
    assert len(queries) >= 5
    assert "course_learner_rankings" in queries
    assert "session_previous_activity_comparison" in queries
    assert "quiz_attempt_sequence_lead_lag" in queries
    assert "rolling_session_metrics" in queries
    assert "overall_learner_rankings" in queries


def test_execute_window_function_queries(populated_window_db):
    """Verify executing window function queries against populated database."""
    results = execute_window_function_queries(db_path=populated_window_db)
    assert isinstance(results, dict)

    # 1. Test Course Learner Rankings (ROW_NUMBER, RANK, AVG OVER)
    course_rank_df = results["course_learner_rankings"]
    assert not course_rank_df.empty
    assert "course_engagement_rank" in course_rank_df.columns
    assert "course_quiz_rank" in course_rank_df.columns
    assert "course_avg_engagement_benchmark" in course_rank_df.columns
    # In C001, S001 has engagement 90.0, S002 has 70.0 -> S001 is rank 1
    c1_ranks = course_rank_df[course_rank_df["target_course_id"] == "C001"]
    assert c1_ranks.iloc[0]["student_id"] == "S001"
    assert c1_ranks.iloc[0]["course_engagement_rank"] == 1

    # 2. Test Previous Session Activity Comparison (LAG)
    lag_session_df = results["session_previous_activity_comparison"]
    assert not lag_session_df.empty
    s1_sessions = lag_session_df[lag_session_df["student_id"] == "S001"]
    # First session has no previous -> prev_session_duration_mins is NaN / None
    assert pd.isna(s1_sessions.iloc[0]["prev_session_duration_mins"])
    # Second session (45 mins) has prev session (30 mins) -> change is +15 mins
    assert s1_sessions.iloc[1]["prev_session_duration_mins"] == 30.0
    assert s1_sessions.iloc[1]["session_duration_change_mins"] == 15.0

    # 3. Test Quiz Progression (LAG & LEAD)
    lead_quiz_df = results["quiz_attempt_sequence_lead_lag"]
    assert not lead_quiz_df.empty
    s1_quizzes = lead_quiz_df[lead_quiz_df["student_id"] == "S001"]
    # Attempt 1: score 60, prev NaN, next 75
    assert pd.isna(s1_quizzes.iloc[0]["previous_attempt_score"])
    assert s1_quizzes.iloc[0]["next_attempt_score"] == 75.0
    # Attempt 2: score 75, prev 60, next 90
    assert s1_quizzes.iloc[1]["previous_attempt_score"] == 60.0
    assert s1_quizzes.iloc[1]["next_attempt_score"] == 90.0
    assert s1_quizzes.iloc[1]["score_improvement_from_prev"] == 15.0

    # 4. Test Rolling Average (AVG OVER)
    rolling_df = results["rolling_session_metrics"]
    assert not rolling_df.empty
    s1_rolling = rolling_df[rolling_df["student_id"] == "S001"]
    # Session 3: dur [30, 45, 60] -> rolling avg is (30+45+60)/3 = 45.0
    assert s1_rolling.iloc[2]["rolling_3_session_avg_duration"] == 45.0

    # 5. Test Overall Platform Leaderboard
    leaderboard_df = results["overall_learner_rankings"]
    assert not leaderboard_df.empty
    assert leaderboard_df.iloc[0]["student_id"] == "S001"
    assert leaderboard_df.iloc[0]["overall_engagement_rank"] == 1


def test_run_window_function_analysis_wrapper(populated_window_db):
    """Verify src.analysis wrapper runs window function analysis cleanly."""
    res = run_window_function_analysis(db_path=populated_window_db)
    assert isinstance(res, dict)
    assert "course_learner_rankings" in res
    assert isinstance(res["course_learner_rankings"], pd.DataFrame)

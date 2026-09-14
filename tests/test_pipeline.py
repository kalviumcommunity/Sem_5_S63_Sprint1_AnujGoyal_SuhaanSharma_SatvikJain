"""Tests for the repeatable end-to-end analytics pipeline entry point."""

import sqlite3

import pandas as pd

from src.pipeline import run_pipeline


def pipeline_source():
    return {
        "students": pd.DataFrame({
            "student_id": ["S001", "S002"],
            "registration_date": ["2026-01-01", "2026-01-02"],
            "age": [20, 22],
            "gender": ["F", "M"],
            "education_level": ["UG", "PG"],
            "device_type": ["Laptop", "Desktop"],
            "target_course_id": ["C101", "C101"],
            "completion_status": ["Completed", "Dropped"],
        }),
        "courses": pd.DataFrame({
            "course_id": ["C101"],
            "course_title": ["Python"],
            "category": ["Programming"],
            "difficulty_level": ["Beginner"],
            "total_modules": [10],
            "total_quizzes": [2],
            "estimated_duration_hours": [20.0],
        }),
        "sessions": pd.DataFrame({
            "session_id": ["SES1", "SES2"],
            "student_id": ["S001", "S002"],
            "course_id": ["C101", "C101"],
            "session_start": ["2026-01-05 10:00:00", "2026-01-05 11:00:00"],
            "session_end": ["2026-01-05 10:30:00", "2026-01-05 11:15:00"],
            "duration_minutes": [30.0, 15.0],
            "active_minutes": [28.0, 10.0],
            "idle_minutes": [2.0, 5.0],
        }),
        "quizzes": pd.DataFrame({
            "quiz_attempt_id": ["QA1", "QA2"],
            "student_id": ["S001", "S002"],
            "course_id": ["C101", "C101"],
            "quiz_id": ["Q1", "Q1"],
            "attempt_number": [1, 1],
            "attempt_date": ["2026-01-06", "2026-01-06"],
            "score_percentage": [90.0, 40.0],
            "time_taken_minutes": [10.0, 12.0],
            "passed": [1, 0],
        }),
    }


def test_pipeline_executes_all_stages_and_generates_outputs(tmp_path):
    result = run_pipeline(
        source_data=pipeline_source(),
        db_path=tmp_path / "analytics.db",
        output_dir=tmp_path / "reports",
    )

    assert result["status"] == "SUCCESS"
    assert result["stages"]["validation"] == "VALID"
    assert result["stages"]["output_generation"] == "SUCCESS"
    assert result["database_status"] == "VALID"
    assert "behavioural_features" in result["processed_datasets"]
    assert all(pd.io.common.file_exists(path) for path in result["output_paths"].values())


def test_pipeline_is_repeatable_without_duplicate_rows(tmp_path):
    db_path = tmp_path / "analytics.db"
    first = run_pipeline(source_data=pipeline_source(), db_path=db_path, generate_outputs=False)
    second = run_pipeline(source_data=pipeline_source(), db_path=db_path, generate_outputs=False)

    assert first["status"] == second["status"] == "SUCCESS"
    assert first["table_row_counts"] == second["table_row_counts"]
    with sqlite3.connect(db_path) as connection:
        count = connection.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    assert count == 2


def test_pipeline_returns_clear_failure_for_incomplete_source(tmp_path):
    result = run_pipeline(
        source_data={"students": pipeline_source()["students"]},
        db_path=tmp_path / "analytics.db",
        generate_outputs=False,
    )

    assert result["status"] == "FAILURE"
    assert "requires source entities" in result["message"]
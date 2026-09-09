"""
Unit tests for Concept #27: SQL Environment & Database Integration.
"""

import sqlite3
import pytest
import pandas as pd
from pathlib import Path
from src.database import (
    init_database,
    get_db_connection,
    query_to_dataframe,
    load_processed_data_to_sqlite,
    validate_database_insertion,
)


@pytest.fixture
def temp_db(tmp_path):
    """Fixture providing temporary SQLite database path."""
    return tmp_path / "test_learning_analytics.db"


def test_init_database_schema(temp_db):
    """Verify schema initialization creates expected SQLite tables."""
    init_database(db_path=temp_db)
    assert temp_db.exists()

    conn = sqlite3.connect(str(temp_db))
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = set(row[0] for row in cursor.fetchall())
    conn.close()

    expected = {"students", "courses", "sessions", "quizzes", "behavioural_features", "student_behaviour_summary"}
    assert expected.issubset(tables), f"Missing tables: {expected - tables}"


def test_load_processed_data_to_sqlite(temp_db):
    """Verify loading DataFrames into SQLite tables."""
    students_df = pd.DataFrame({
        "student_id": ["S001", "S002"],
        "registration_date": ["2026-01-01", "2026-01-02"],
        "age": [22, 25],
        "gender": ["Female", "Male"],
        "education_level": ["Undergraduate", "Postgraduate"],
        "device_type": ["Laptop", "Desktop"],
        "target_course_id": ["C001", "C002"],
        "completion_status": ["Completed", "In Progress"]
    })

    courses_df = pd.DataFrame({
        "course_id": ["C001", "C002"],
        "course_title": ["Python", "SQL"],
        "category": ["Data Science", "Database"],
        "total_modules": [10, 8],
        "total_quizzes": [5, 4],
        "estimated_duration_hours": [20.0, 15.0]
    })

    datasets = {
        "students": students_df,
        "courses": courses_df
    }

    inserted = load_processed_data_to_sqlite(datasets, db_path=temp_db)
    assert inserted["students"] == 2
    assert inserted["courses"] == 2

    res_students = query_to_dataframe("SELECT * FROM students;", db_path=temp_db)
    assert len(res_students) == 2
    assert res_students.iloc[0]["student_id"] == "S001"


def test_validate_database_insertion(temp_db):
    """Verify database insertion validation logic."""
    init_database(db_path=temp_db)

    students_df = pd.DataFrame({"student_id": ["S001"], "registration_date": ["2026-01-01"]})
    load_processed_data_to_sqlite({"students": students_df}, db_path=temp_db)

    report = validate_database_insertion(
        db_path=temp_db,
        expected_tables=["students", "courses"]
    )

    assert report["status"] == "VALID"
    assert report["table_row_counts"]["students"] == 1
    assert report["table_row_counts"]["courses"] == 0
    assert "students" in report["existing_tables"]
    assert "courses" in report["existing_tables"]


def test_query_to_dataframe(temp_db):
    """Verify executing SQL query returns correct DataFrame results."""
    init_database(db_path=temp_db)
    conn = get_db_connection(temp_db)
    conn.execute("INSERT INTO courses VALUES ('C101', 'Intro to ML', 'AI', 12, 6, 30.0, 'Intermediate');")
    conn.commit()
    conn.close()

    df = query_to_dataframe("SELECT course_id, course_title, category FROM courses WHERE course_id = 'C101';", db_path=temp_db)
    assert not df.empty
    assert len(df) == 1
    assert df.iloc[0]["course_title"] == "Intro to ML"
    assert df.iloc[0]["category"] == "AI"

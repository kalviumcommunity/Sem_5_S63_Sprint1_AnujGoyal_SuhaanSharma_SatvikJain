"""
Unit tests for Concept #5: CSV & JSON Data Ingestion.
Tests CSV and JSON ingestion for students, courses, sessions, and quizzes.
"""

import json
import pytest
from pathlib import Path
import pandas as pd

from src.utils import DataLoadError, ValidationError
from src.ingestion import (
    load_dataset,
    ingest_entity,
    ingest_all_entities,
    read_json_flexible,
    SUPPORTED_ENTITIES
)


@pytest.fixture
def mock_datasets():
    """Provides sample valid data for all 4 project entities."""
    return {
        "students": pd.DataFrame({
            "student_id": ["S001", "S002"],
            "registration_date": ["2026-01-01", "2026-01-02"],
            "age": [20, 22],
            "gender": ["F", "M"],
            "education_level": ["Undergraduate", "Postgraduate"],
            "device_type": ["Laptop", "Desktop"],
            "target_course_id": ["C101", "C102"],
            "completion_status": ["Completed", "In Progress"]
        }),
        "courses": pd.DataFrame({
            "course_id": ["C101", "C102"],
            "course_title": ["Python for Data Science", "Machine Learning Foundations"],
            "category": ["Data Science", "AI"],
            "total_modules": [10, 15],
            "total_quizzes": [4, 6],
            "estimated_duration_hours": [20.0, 35.0]
        }),
        "sessions": pd.DataFrame({
            "session_id": ["SES001", "SES002"],
            "student_id": ["S001", "S002"],
            "course_id": ["C101", "C102"],
            "session_start": ["2026-01-05 10:00:00", "2026-01-05 11:00:00"],
            "session_end": ["2026-01-05 10:45:00", "2026-01-05 11:30:00"],
            "duration_minutes": [45.0, 30.0],
            "active_minutes": [40.0, 25.0],
            "idle_minutes": [5.0, 5.0]
        }),
        "quizzes": pd.DataFrame({
            "quiz_attempt_id": ["Q001", "Q002"],
            "student_id": ["S001", "S002"],
            "course_id": ["C101", "C102"],
            "quiz_id": ["QUIZ_1", "QUIZ_1"],
            "attempt_number": [1, 1],
            "attempt_date": ["2026-01-08", "2026-01-09"],
            "score_percentage": [85.0, 92.5],
            "time_taken_minutes": [15.0, 12.0],
            "passed": [1, 1]
        })
    }


def test_csv_ingestion_all_entities(tmp_path, mock_datasets):
    """Test CSV ingestion for students, courses, sessions, and quizzes."""
    for entity, df in mock_datasets.items():
        csv_file = tmp_path / f"{entity}.csv"
        df.to_csv(csv_file, index=False)

        loaded_df = load_dataset(csv_file, validate_source=True, entity_name=entity)
        assert len(loaded_df) == 2
        assert list(loaded_df.columns) == list(df.columns)


def test_json_ingestion_all_entities(tmp_path, mock_datasets):
    """Test JSON ingestion for students, courses, sessions, and quizzes."""
    for entity, df in mock_datasets.items():
        json_file = tmp_path / f"{entity}.json"
        df.to_json(json_file, orient="records")

        loaded_df = load_dataset(json_file, validate_source=True, entity_name=entity)
        assert len(loaded_df) == 2
        assert list(loaded_df.columns) == list(df.columns)


def test_json_ingestion_dict_orientation(tmp_path):
    """Test flexible JSON ingestion for key-value dictionary formats."""
    dict_data = {
        "S001": {"student_id": "S001", "age": 21, "completion_status": "Completed"},
        "S002": {"student_id": "S002", "age": 24, "completion_status": "In Progress"}
    }
    json_path = tmp_path / "dict_students.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(dict_data, f)

    df = read_json_flexible(json_path)
    assert len(df) == 2
    assert "student_id" in df.columns
    assert "age" in df.columns


def test_ingest_entity_auto_discovery(tmp_path, mock_datasets):
    """Test auto-discovery of CSV and JSON entity files in a directory."""
    # Save students as CSV and courses as JSON
    mock_datasets["students"].to_csv(tmp_path / "students.csv", index=False)
    mock_datasets["courses"].to_json(tmp_path / "courses.json", orient="records")

    students_df = ingest_entity("students", directory=tmp_path)
    courses_df = ingest_entity("courses", directory=tmp_path)

    assert len(students_df) == 2
    assert len(courses_df) == 2


def test_ingest_all_entities(tmp_path, mock_datasets):
    """Test batch ingestion of all entities."""
    for entity, df in mock_datasets.items():
        df.to_csv(tmp_path / f"{entity}.csv", index=False)

    all_data = ingest_all_entities(directory=tmp_path, validate_schema=True)
    for entity in SUPPORTED_ENTITIES:
        assert entity in all_data
        assert len(all_data[entity]) == 2


def test_ingestion_corrupted_json(tmp_path):
    """Test graceful failure when ingesting a corrupted JSON file."""
    corrupted_json = tmp_path / "corrupted.json"
    corrupted_json.write_text("{ incomplete json ...", encoding="utf-8")

    with pytest.raises(DataLoadError):
        load_dataset(corrupted_json)


def test_ingestion_invalid_format(tmp_path):
    """Test graceful rejection of unsupported file extensions."""
    invalid_file = tmp_path / "data.unsupported"
    invalid_file.write_text("random binary content", encoding="utf-8")

    with pytest.raises(DataLoadError):
        load_dataset(invalid_file)


def test_ingestion_schema_validation_failure(tmp_path):
    """Test that invalid entity schema triggers ValidationError during ingestion."""
    invalid_students = pd.DataFrame({"unrelated_col": [1, 2]})
    invalid_csv = tmp_path / "students.csv"
    invalid_students.to_csv(invalid_csv, index=False)

    with pytest.raises(ValidationError):
        load_dataset(invalid_csv, entity_name="students")

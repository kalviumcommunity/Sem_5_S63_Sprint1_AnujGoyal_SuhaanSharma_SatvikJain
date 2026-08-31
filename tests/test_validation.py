"""
Unit tests for Concept #4: Dataset Intake & Source Validation.
Tests file source validation, schema validation, empty datasets, entity models, and pipeline intake.
"""

import pytest
from pathlib import Path
import pandas as pd
from src.utils import ValidationError
from src.validation import (
    validate_file_source,
    validate_dataset_schema,
    validate_dataframe,
    validate_entity_dataset,
    validate_intake_pipeline,
    ENTITY_SCHEMAS
)


@pytest.fixture
def valid_students_df():
    """Returns a valid students DataFrame matching the required entity schema."""
    return pd.DataFrame({
        "student_id": ["S001", "S002"],
        "registration_date": ["2026-01-01", "2026-01-02"],
        "age": [20, 22],
        "gender": ["F", "M"],
        "education_level": ["Undergraduate", "Postgraduate"],
        "device_type": ["Laptop", "Desktop"],
        "target_course_id": ["C101", "C102"],
        "completion_status": ["Completed", "In Progress"]
    })


@pytest.fixture
def valid_sessions_df():
    """Returns a valid sessions DataFrame matching the required entity schema."""
    return pd.DataFrame({
        "session_id": ["SES001", "SES002"],
        "student_id": ["S001", "S002"],
        "course_id": ["C101", "C102"],
        "session_start": ["2026-01-05 10:00:00", "2026-01-05 11:00:00"],
        "session_end": ["2026-01-05 10:45:00", "2026-01-05 11:30:00"],
        "duration_minutes": [45.0, 30.0],
        "active_minutes": [40.0, 25.0],
        "idle_minutes": [5.0, 5.0]
    })


def test_validate_file_source_valid(tmp_path):
    """Test validating an existing, valid CSV file."""
    test_csv = tmp_path / "valid.csv"
    test_csv.write_text("col1,col2\nval1,val2\n", encoding="utf-8")

    result = validate_file_source(test_csv)
    assert result.is_valid is True
    assert len(result.errors) == 0


def test_validate_file_source_non_existent():
    """Test validating a missing file path."""
    result = validate_file_source("non_existent_source_path.csv")
    assert result.is_valid is False
    assert any("does not exist" in err for err in result.errors)


def test_validate_file_source_empty_file(tmp_path):
    """Test validating a 0-byte empty file."""
    empty_file = tmp_path / "empty.csv"
    empty_file.touch()

    result = validate_file_source(empty_file)
    assert result.is_valid is False
    assert any("0 bytes" in err for err in result.errors)


def test_validate_file_source_unsupported_format(tmp_path):
    """Test validating a file with an unsupported extension."""
    invalid_ext = tmp_path / "data.docx"
    invalid_ext.write_text("content", encoding="utf-8")

    result = validate_file_source(invalid_ext)
    assert result.is_valid is False
    assert any("Unsupported file format" in err for err in result.errors)


def test_validate_dataset_schema_valid(valid_students_df):
    """Test validating a valid dataframe schema."""
    result = validate_dataset_schema(
        df=valid_students_df,
        required_columns=ENTITY_SCHEMAS["students"],
        dataset_name="Students"
    )
    assert result.is_valid is True
    assert result.row_count == 2
    assert result.column_count == 8
    assert len(result.missing_columns) == 0


def test_validate_dataset_schema_missing_columns(valid_students_df):
    """Test schema validation fails when required columns are absent."""
    incomplete_df = valid_students_df.drop(columns=["age", "completion_status"])
    result = validate_dataset_schema(
        df=incomplete_df,
        required_columns=ENTITY_SCHEMAS["students"],
        dataset_name="Students"
    )
    assert result.is_valid is False
    assert "age" in result.missing_columns
    assert "completion_status" in result.missing_columns


def test_validate_dataset_schema_empty_dataframe():
    """Test schema validation fails on empty DataFrames."""
    empty_df = pd.DataFrame()
    result = validate_dataset_schema(empty_df, required_columns=["id"], dataset_name="Empty")
    assert result.is_valid is False
    assert any("empty" in err for err in result.errors)


def test_validate_dataset_schema_min_rows_threshold(valid_students_df):
    """Test validation fails when row count is below minimum required rows."""
    result = validate_dataset_schema(
        df=valid_students_df,
        required_columns=ENTITY_SCHEMAS["students"],
        dataset_name="Students",
        min_rows=10
    )
    assert result.is_valid is False
    assert any("below required minimum" in err for err in result.errors)


def test_validate_entity_dataset_success(valid_students_df):
    """Test entity validation for students dataset."""
    result = validate_entity_dataset(valid_students_df, entity_name="students")
    assert result.is_valid is True


def test_validate_entity_dataset_raise_on_error():
    """Test that validate_entity_dataset raises ValidationError when configured."""
    invalid_df = pd.DataFrame({"dummy": [1, 2]})
    with pytest.raises(ValidationError):
        validate_entity_dataset(invalid_df, entity_name="students", raise_on_error=True)


def test_validate_entity_dataset_unknown_entity(valid_students_df):
    """Test that validating an unknown entity type raises ValidationError."""
    with pytest.raises(ValidationError):
        validate_entity_dataset(valid_students_df, entity_name="unknown_entity")


def test_validate_intake_pipeline(valid_students_df, valid_sessions_df):
    """Test intake pipeline validation across multiple entity datasets."""
    datasets = {
        "students": valid_students_df,
        "sessions": valid_sessions_df
    }
    report = validate_intake_pipeline(datasets, raise_on_error=False)
    assert report["status"] == "VALID"
    assert report["overall_valid"] is True
    assert report["entity_reports"]["students"]["is_valid"] is True
    assert report["entity_reports"]["sessions"]["is_valid"] is True


def test_validate_intake_pipeline_invalid_entity(valid_students_df):
    """Test intake pipeline catches invalid datasets and reports failures."""
    datasets = {
        "students": valid_students_df,
        "sessions": pd.DataFrame({"corrupted": [1, 2]})
    }
    report = validate_intake_pipeline(datasets, raise_on_error=False)
    assert report["status"] == "INVALID"
    assert report["overall_valid"] is False
    assert report["entity_reports"]["sessions"]["is_valid"] is False

    with pytest.raises(ValidationError):
        validate_intake_pipeline(datasets, raise_on_error=True)

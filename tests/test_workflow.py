"""
Unit tests for Concept #3: Python Data Workflow Foundations.
Tests loading, inspection, transformation, storage, and orchestration.
"""

import pytest
import sqlite3
from pathlib import Path
import pandas as pd
import numpy as np

from src.utils import DataLoadError, TransformationError, DataExportError
from src.ingestion import load_dataset, load_raw_dataset, load_all_raw_data
from src.inspection import inspect_dataframe, get_column_summary
from src.transformation import (
    standardize_column_names,
    cast_column_types,
    parse_datetime_columns,
    derive_column,
)
from src.storage import save_dataframe, save_to_database, export_processed_dataset
from src.workflow import DataWorkflow


@pytest.fixture
def sample_students_df():
    """Provides a sample student dataframe for workflow testing."""
    return pd.DataFrame({
        " Student ID ": ["S001", "S002", "S003", "S003"],
        "Registration Date": ["2026-01-10", "2026-01-12", "2026-01-15", "2026-01-15"],
        "Age": ["21", "24", "22", "22"],
        "Course Modules Completed": [5, 12, 0, 0],
        "Quiz Score %": [85.5, 92.0, 45.0, 45.0]
    })


def test_load_dataset_csv(tmp_path, sample_students_df):
    """Test loading a CSV file using load_dataset."""
    csv_file = tmp_path / "test_students.csv"
    sample_students_df.to_csv(csv_file, index=False)

    loaded_df = load_dataset(csv_file)
    assert len(loaded_df) == 4
    assert list(loaded_df.columns) == list(sample_students_df.columns)


def test_load_dataset_json(tmp_path, sample_students_df):
    """Test loading a JSON file using load_dataset."""
    json_file = tmp_path / "test_students.json"
    sample_students_df.to_json(json_file, orient="records")

    loaded_df = load_dataset(json_file)
    assert len(loaded_df) == 4


def test_load_dataset_missing_file():
    """Test that missing files raise DataLoadError."""
    with pytest.raises(DataLoadError):
        load_dataset("non_existent_file_xyz.csv")


def test_inspect_dataframe(sample_students_df):
    """Test structural inspection of a DataFrame."""
    inspection = inspect_dataframe(sample_students_df, dataset_name="TestStudents")
    assert inspection["status"] == "POPULATED"
    assert inspection["row_count"] == 4
    assert inspection["column_count"] == 5
    assert inspection["duplicate_rows"] == 1
    assert inspection["memory_usage_mb"] > 0
    assert "Age" in inspection["null_counts"]


def test_get_column_summary(sample_students_df):
    """Test column-level profiling summary."""
    summary = get_column_summary(sample_students_df)
    assert "Age" in summary
    assert summary["Age"]["unique_count"] == 3


def test_standardize_column_names(sample_students_df):
    """Test column name normalization and sanitization."""
    standardized = standardize_column_names(sample_students_df)
    expected_cols = [
        "student_id",
        "registration_date",
        "age",
        "course_modules_completed",
        "quiz_score"
    ]
    assert list(standardized.columns) == expected_cols


def test_cast_column_types():
    """Test safe column casting."""
    df = pd.DataFrame({"id": ["1", "2", "3"], "score": ["88.5", "90.0", "75.2"]})
    casted = cast_column_types(df, {"id": "int", "score": "float"})
    assert pd.api.types.is_integer_dtype(casted["id"])
    assert pd.api.types.is_float_dtype(casted["score"])


def test_parse_datetime_columns():
    """Test parsing datetime columns."""
    df = pd.DataFrame({"reg_date": ["2026-01-01", "2026-02-15", "invalid_date"]})
    parsed = parse_datetime_columns(df, ["reg_date"])
    assert pd.api.types.is_datetime64_any_dtype(parsed["reg_date"])
    assert pd.isna(parsed["reg_date"].iloc[2])  # Coerced invalid date


def test_derive_column():
    """Test deriving a new feature column."""
    df = pd.DataFrame({"total_modules": [10, 20], "completed_modules": [5, 15]})
    derived = derive_column(
        df,
        "progress_ratio",
        lambda d: d["completed_modules"] / d["total_modules"]
    )
    assert "progress_ratio" in derived.columns
    assert derived["progress_ratio"].iloc[0] == 0.5
    assert derived["progress_ratio"].iloc[1] == 0.75


def test_save_dataframe(tmp_path, sample_students_df):
    """Test saving a DataFrame to CSV and JSON."""
    out_csv = tmp_path / "output" / "saved.csv"
    out_json = tmp_path / "output" / "saved.json"

    saved_csv_path = save_dataframe(sample_students_df, out_csv)
    saved_json_path = save_dataframe(sample_students_df, out_json)

    assert saved_csv_path.exists()
    assert saved_json_path.exists()
    assert len(pd.read_csv(saved_csv_path)) == 4


def test_save_to_database(tmp_path, sample_students_df):
    """Test saving a DataFrame into an SQLite table."""
    test_db = tmp_path / "workflow_test.db"
    clean_df = standardize_column_names(sample_students_df)
    save_to_database(clean_df, table_name="test_students", db_path=test_db)

    with sqlite3.connect(str(test_db)) as conn:
        result = pd.read_sql_query("SELECT count(*) as count FROM test_students", conn)
        assert result["count"].iloc[0] == 4


def test_data_workflow_orchestrator(tmp_path, sample_students_df):
    """Test end-to-end DataWorkflow pipeline execution."""
    workflow = DataWorkflow(name="TestWorkflow")
    raw_dict = {"students": sample_students_df}

    result = workflow.run_full_pipeline(
        source=raw_dict,
        output_dir=tmp_path,
        save_to_db=False
    )

    assert result["status"] == "SUCCESS"
    assert "students" in result["datasets_loaded"]
    assert "students" in result["datasets_transformed"]
    assert "students" in result["saved_outputs"]
    assert (tmp_path / "students_processed.csv").exists()

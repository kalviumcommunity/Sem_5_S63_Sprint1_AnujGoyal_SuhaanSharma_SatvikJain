"""
Test suite verifying the development environment and workspace setup.
"""

import sys
import sqlite3
import pytest
from pathlib import Path
from src.utils import (
    PROJECT_ROOT,
    DATA_DIR,
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    DATABASE_DIR,
    REPORTS_DIR,
    SQL_DIR,
    DB_PATH,
    ensure_directories_exist,
)
from src.database import init_database, get_db_connection, query_to_dataframe
from src.pipeline import run_pipeline
from src.validation import validate_dataframe
from src.cleaning import clean_dataframe
import pandas as pd


def test_python_version():
    """Verify that Python version meets minimum requirement (>=3.10)."""
    assert sys.version_info >= (3, 10), f"Python version too low: {sys.version}"


def test_core_dependencies():
    """Verify that all required core libraries can be imported."""
    import pandas
    import numpy
    import plotly
    import streamlit

    assert pandas.__version__ is not None
    assert numpy.__version__ is not None
    assert plotly.__version__ is not None
    assert streamlit.__version__ is not None


def test_project_structure_directories():
    """Verify that all standard project directories exist or can be created."""
    ensure_directories_exist()
    assert PROJECT_ROOT.exists()
    assert DATA_DIR.exists()
    assert RAW_DATA_DIR.exists()
    assert PROCESSED_DATA_DIR.exists()
    assert DATABASE_DIR.exists()
    assert REPORTS_DIR.exists()
    assert SQL_DIR.exists()


def test_database_initialization(tmp_path):
    """Verify that SQLite database schema initializes tables correctly."""
    test_db = tmp_path / "test_analytics.db"
    init_database(db_path=test_db)
    assert test_db.exists()

    conn = sqlite3.connect(str(test_db))
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()

    expected_tables = ["courses", "students", "sessions", "quizzes", "student_behaviour_summary"]
    for table in expected_tables:
        assert table in tables, f"Expected table '{table}' missing from database."


def test_validation_module():
    """Verify data validation behavior on sample dataframe."""
    sample_df = pd.DataFrame({"student_id": ["S001", "S002"], "score": [85, 90]})
    report = validate_dataframe(sample_df, required_columns=["student_id", "score"])
    assert report["status"] == "VALID"
    assert report["row_count"] == 2

    invalid_report = validate_dataframe(sample_df, required_columns=["student_id", "missing_col"])
    assert invalid_report["status"] == "INVALID"
    assert "missing_col" in invalid_report["missing_columns"]


def test_cleaning_module():
    """Verify data cleaning deduplication and whitespace trimming."""
    sample_df = pd.DataFrame({
        "student_id": [" S001 ", "S002", "S002"],
        "category": [" Data ", " AI", " AI"]
    })
    cleaned = clean_dataframe(sample_df)
    assert len(cleaned) == 2
    assert cleaned.iloc[0]["student_id"] == "S001"
    assert cleaned.iloc[0]["category"] == "Data"


def test_pipeline_execution():
    """Verify that pipeline runs without errors."""
    result = run_pipeline()
    assert result["status"] == "SUCCESS"

"""
Unit tests for Concept #7: Data Dictionary & Business Context Mapping.
Tests dictionary completeness, column metadata, business definitions, and programmatic DataFrame exports.
"""

import pytest
from pathlib import Path
import pandas as pd

from src.data_dictionary import (
    DATA_DICTIONARY,
    get_data_dictionary_dataframe,
    get_column_business_context
)


def test_data_dictionary_structure():
    """Verify that all core entities and derived metrics are present in the dictionary."""
    expected_sections = ["students", "courses", "sessions", "quizzes", "derived_metrics"]
    for section in expected_sections:
        assert section in DATA_DICTIONARY, f"Missing section '{section}' in DATA_DICTIONARY"


def test_key_fields_documented():
    """Verify that all required key fields are documented with complete business metadata."""
    key_fields = [
        "student_id",
        "course_id",
        "session_date",
        "session_duration",
        "quiz_score",
        "progress_pct",
        "completion_status"
    ]
    for field in key_fields:
        context = get_column_business_context(field)
        assert context is not None, f"Field '{field}' not found in data dictionary"
        assert "business_meaning" in context and len(context["business_meaning"]) > 0
        assert "data_type" in context and len(context["data_type"]) > 0
        assert "valid_range" in context and len(context["valid_range"]) > 0
        assert "analysis_use" in context and len(context["analysis_use"]) > 0


def test_get_data_dictionary_dataframe():
    """Verify that get_data_dictionary_dataframe returns a valid populated DataFrame."""
    df = get_data_dictionary_dataframe()
    assert isinstance(df, pd.DataFrame)
    assert len(df) >= 20  # All entity columns + derived metrics
    expected_cols = [
        "Entity / Dataset",
        "Column Name",
        "Data Type",
        "Business Meaning",
        "Source Dataset",
        "Valid Range / Values",
        "Required",
        "Analysis Application"
    ]
    for col in expected_cols:
        assert col in df.columns, f"Missing expected column '{col}' in dictionary DataFrame"


def test_get_data_dictionary_dataframe_single_entity():
    """Verify filtering data dictionary DataFrame by single entity."""
    students_dict_df = get_data_dictionary_dataframe(entity_name="students")
    assert isinstance(students_dict_df, pd.DataFrame)
    assert len(students_dict_df) == len(DATA_DICTIONARY["students"])
    assert (students_dict_df["Entity / Dataset"] == "students").all()


def test_docs_data_dictionary_file_exists():
    """Verify that docs/data_dictionary.md exists and contains the required content."""
    doc_path = Path("docs/data_dictionary.md")
    assert doc_path.exists(), "docs/data_dictionary.md does not exist"
    content = doc_path.read_text(encoding="utf-8")
    assert "student_id" in content
    assert "completion_status" in content
    assert "session_duration" in content
    assert "quiz_score" in content

"""
Unit tests for Concept #9: Data Type Enforcement & Standardisation.
Tests percentage parsing, boolean normalization, ID formatting, category mapping,
timestamp standardisation, and entity-level type enforcement.
"""

import pytest
import pandas as pd
import numpy as np

from src.standardization import (
    clean_percentage_value,
    clean_boolean_flag,
    standardize_identifiers,
    standardize_dates,
    standardize_timestamps,
    standardize_categories,
    standardize_entity
)


def test_clean_percentage_value():
    """Test percentage conversion from multiple string and numeric representations."""
    assert clean_percentage_value("85%") == 85.0
    assert clean_percentage_value(" 92.5 % ") == 92.5
    assert clean_percentage_value("100%") == 100.0
    assert clean_percentage_value(0.75) == 75.0
    assert clean_percentage_value(88.0) == 88.0
    assert clean_percentage_value(None) is None
    assert clean_percentage_value("") is None
    assert clean_percentage_value("invalid_str") is None


def test_clean_boolean_flag():
    """Test boolean normalization into integer 1 or 0."""
    # Truthy
    assert clean_boolean_flag(True) == 1
    assert clean_boolean_flag("True") == 1
    assert clean_boolean_flag("true") == 1
    assert clean_boolean_flag("1") == 1
    assert clean_boolean_flag(1) == 1
    assert clean_boolean_flag("PASS") == 1
    assert clean_boolean_flag("yes") == 1

    # Falsy
    assert clean_boolean_flag(False) == 0
    assert clean_boolean_flag("False") == 0
    assert clean_boolean_flag("0") == 0
    assert clean_boolean_flag(0) == 0
    assert clean_boolean_flag("FAIL") == 0
    assert clean_boolean_flag("no") == 0
    assert clean_boolean_flag(None) == 0


def test_standardize_identifiers():
    """Test uppercase and stripped formatting of ID fields."""
    df = pd.DataFrame({
        "student_id": [" s001 ", "stu_99", "s102"],
        "course_id": ["c101", " c102 ", "crs_ai"]
    })
    res = standardize_identifiers(df, ["student_id", "course_id"])

    assert list(res["student_id"]) == ["S001", "STU_99", "S102"]
    assert list(res["course_id"]) == ["C101", "C102", "CRS_AI"]


def test_standardize_dates():
    """Test standardizing messy dates to datetime and ISO format."""
    df = pd.DataFrame({
        "reg_date": ["2026/08/01", "2026-08-15", "01-08-2026"]
    })
    dt_df = standardize_dates(df, ["reg_date"], as_iso_string=False)
    assert pd.api.types.is_datetime64_any_dtype(dt_df["reg_date"])

    iso_df = standardize_dates(df, ["reg_date"], as_iso_string=True)
    assert iso_df["reg_date"].iloc[0] == "2026-08-01"


def test_standardize_timestamps():
    """Test timestamp standardisation."""
    df = pd.DataFrame({
        "start_time": ["2026-08-01 10:30:00", "2026-08-01T14:15:00"]
    })
    dt_df = standardize_timestamps(df, ["start_time"], as_iso_string=False)
    assert pd.api.types.is_datetime64_any_dtype(dt_df["start_time"])


def test_standardize_categories():
    """Test categorical synonym mapping across student demographic and status attributes."""
    df = pd.DataFrame({
        "completion_status": ["completed", "in-progress", "dropout", "ongoing"],
        "gender": ["m", "female", "nb", "woman"],
        "education_level": ["undergrad", "postgrad", "high school", "bachelors"],
        "device_type": ["pc", "laptop", "smartphone", "ipad"]
    })
    std_df = standardize_categories(df)

    assert list(std_df["completion_status"]) == ["Completed", "In Progress", "Dropped", "In Progress"]
    assert list(std_df["gender"]) == ["Male", "Female", "Non-Binary", "Female"]
    assert list(std_df["education_level"]) == ["Undergraduate", "Postgraduate", "High School", "Undergraduate"]
    assert list(std_df["device_type"]) == ["Desktop", "Laptop", "Mobile", "Tablet"]


def test_standardize_entity_students():
    """Test full entity standardization for students."""
    messy_students = pd.DataFrame({
        "student_id": [" s101 ", "s102"],
        "registration_date": ["2026/01/10", "2026/01/15"],
        "age": ["21", "24.0"],
        "gender": ["m", "f"],
        "education_level": ["undergrad", "postgrad"],
        "device_type": ["pc", "smartphone"],
        "target_course_id": [" c101 ", "c102"],
        "completion_status": ["completed", "in-progress"]
    })
    clean_df = standardize_entity(messy_students, entity_name="students")

    assert clean_df["student_id"].tolist() == ["S101", "S102"]
    assert clean_df["target_course_id"].tolist() == ["C101", "C102"]
    assert pd.api.types.is_integer_dtype(clean_df["age"])
    assert clean_df["gender"].tolist() == ["Male", "Female"]
    assert clean_df["completion_status"].tolist() == ["Completed", "In Progress"]


def test_standardize_entity_quizzes():
    """Test full entity standardization for quizzes."""
    messy_quizzes = pd.DataFrame({
        "quiz_attempt_id": [" qa01 ", "qa02"],
        "student_id": ["s001", "s002"],
        "course_id": ["c101", "c101"],
        "quiz_id": ["qz_1", "qz_1"],
        "attempt_number": ["1", "2"],
        "attempt_date": ["2026/02/01", "2026/02/02"],
        "score_percentage": ["85%", " 92.5 % "],
        "time_taken_minutes": ["14.5", "18"],
        "passed": ["PASS", "true"]
    })
    clean_df = standardize_entity(messy_quizzes, entity_name="quizzes")

    assert clean_df["quiz_attempt_id"].tolist() == ["QA01", "QA02"]
    assert clean_df["score_percentage"].tolist() == [85.0, 92.5]
    assert clean_df["passed"].tolist() == [1, 1]
    assert pd.api.types.is_integer_dtype(clean_df["passed"])

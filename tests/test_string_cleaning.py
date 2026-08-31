"""
Unit tests for Concept #11: String Cleaning & Text Normalisation.
Tests whitespace normalization, casing standardisation, technical acronym preservation,
category label canonical mapping, and DataFrame text cleaning integration.
"""

import pytest
import pandas as pd
import numpy as np

from src.text_cleaning import (
    normalize_whitespace,
    clean_text_string,
    clean_course_title,
    clean_category_label,
    clean_text_dataframe
)
from src.cleaning import clean_dataframe


def test_normalize_whitespace():
    """Test whitespace stripping, multi-space collapse, and special space characters."""
    assert normalize_whitespace("   Data Science   ") == "Data Science"
    assert normalize_whitespace("Machine   Learning") == "Machine Learning"
    assert normalize_whitespace("Cloud\tComputing\nAnalytics\r") == "Cloud Computing Analytics"
    assert normalize_whitespace("Data\xa0Science") == "Data Science"
    assert normalize_whitespace(None) == ""
    assert normalize_whitespace(np.nan) == ""


def test_clean_text_string_title_casing():
    """Test standard title casing with grammatical lowercasing."""
    assert clean_text_string("intro to python programming") == "Intro to Python Programming"
    assert clean_text_string("fundamentals of web development") == "Fundamentals of Web Development"
    assert clean_text_string("data structures and algorithms") == "Data Structures and Algorithms"


def test_clean_text_string_tech_acronyms():
    """Test technical acronym capitalization preservation."""
    assert clean_text_string("intro to ai and ml") == "Intro to AI and ML"
    assert clean_text_string("advanced sql queries") == "Advanced SQL Queries"
    assert clean_text_string("cloud architecture with aws and gcp") == "Cloud Architecture with AWS and GCP"


def test_clean_course_title():
    """Test course catalog title cleaning."""
    assert clean_course_title("  intro  to   machine  learning (ai/ml) ") == "Intro to Machine Learning (AI/ML)"
    assert clean_course_title(None) == "Untitled Course"
    assert clean_course_title("full-stack   web  development with js and html") == "Full-Stack Web Development with JS and HTML"


def test_clean_category_label():
    """Test category label canonical normalization."""
    assert clean_category_label("data science") == "Data Science"
    assert clean_category_label(" DATA SCIENCE ") == "Data Science"
    assert clean_category_label("data_science") == "Data Science"
    assert clean_category_label("ds") == "Data Science"
    assert clean_category_label("ai/ml") == "AI & Machine Learning"
    assert clean_category_label("web dev") == "Web Development"
    assert clean_category_label("cyber security") == "Cybersecurity"
    assert clean_category_label("cloud") == "Cloud Computing"
    assert clean_category_label(None) == "General"


def test_clean_text_dataframe_courses():
    """Test clean_text_dataframe across course records."""
    df = pd.DataFrame({
        "course_id": ["C101", "C102"],
        "course_title": ["  intro  to  data  science  ", "advanced   ai  &  ml   "],
        "category": ["data_science", "ai/ml"]
    })
    cleaned = clean_text_dataframe(df, entity_name="courses")

    assert cleaned["course_title"].tolist() == ["Intro to Data Science", "Advanced AI & ML"]
    assert cleaned["category"].tolist() == ["Data Science", "AI & Machine Learning"]


def test_clean_dataframe_integration_text():
    """Test clean_dataframe runs string cleaning seamlessly."""
    df = pd.DataFrame({
        "course_id": ["C101"],
        "course_title": ["  python   for   data  science  "],
        "category": [" ds "]
    })
    res = clean_dataframe(df, entity_name="courses")
    assert res["course_title"].iloc[0] == "Python for Data Science"
    assert res["category"].iloc[0] == "Data Science"

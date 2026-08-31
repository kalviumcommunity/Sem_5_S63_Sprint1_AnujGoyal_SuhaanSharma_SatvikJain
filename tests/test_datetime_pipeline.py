"""
Unit tests for Concept #12: Date & Time Transformation Pipeline.
Tests timestamp parsing, timezone stripping, date component extraction (day, week, month, weekday, hour),
time-of-day behavioral binning, weekend flags, and entity-level datetime enrichment.
"""

import pytest
import pandas as pd
import numpy as np

from src.datetime_pipeline import (
    categorize_day_part,
    parse_datetime_series,
    extract_datetime_features,
    calculate_session_duration_minutes,
    transform_entity_datetimes,
    transform_all_datetimes
)


def test_categorize_day_part():
    """Test study time-of-day categorization."""
    assert categorize_day_part(8) == "Morning"
    assert categorize_day_part(11.5) == "Morning"
    assert categorize_day_part(14) == "Afternoon"
    assert categorize_day_part(19) == "Evening"
    assert categorize_day_part(23) == "Night"
    assert categorize_day_part(2) == "Night"
    assert categorize_day_part(None) == "Unknown"
    assert categorize_day_part(np.nan) == "Unknown"


def test_parse_datetime_series():
    """Test robust datetime parsing with timezone-stripping."""
    raw = pd.Series([
        "2026-02-01T10:30:00Z",
        "2026/02/15 14:00:00",
        "2026-03-01",
        "corrupted-timestamp",
        None
    ])
    parsed = parse_datetime_series(raw, strip_timezone=True)

    assert pd.api.types.is_datetime64_any_dtype(parsed)
    assert parsed.dt.tz is None  # Timezone naive
    assert parsed.iloc[0] == pd.Timestamp("2026-02-01 10:30:00")
    assert pd.isna(parsed.iloc[3])  # Corrupted coerced to NaT without error


def test_extract_datetime_features():
    """Test extraction of all requested temporal features."""
    # 2026-08-01 is a Saturday, 2026-08-03 is a Monday
    df = pd.DataFrame({
        "timestamp": ["2026-08-01 09:15:00", "2026-08-03 20:45:00"]
    })
    enriched = extract_datetime_features(df, timestamp_column="timestamp", prefix="act_", include_time=True)

    # 1. Date & Year/Month/Day
    assert enriched["act_date"].tolist() == ["2026-08-01", "2026-08-03"]
    assert enriched["act_year"].tolist() == [2026, 2026]
    assert enriched["act_month"].tolist() == [8, 8]
    assert enriched["act_month_name"].tolist() == ["August", "August"]
    assert enriched["act_day"].tolist() == [1, 3]

    # 2. Weekday & Weekend flag
    assert enriched["act_weekday_name"].tolist() == ["Saturday", "Monday"]
    assert enriched["act_is_weekend"].tolist() == [1, 0]  # Saturday=1, Monday=0

    # 3. ISO Week & Week Number
    assert (enriched["act_week"] > 0).all()
    assert (enriched["act_week_number"] == enriched["act_week"]).all()

    # 4. Hour & Day Part
    assert enriched["act_hour"].tolist() == [9, 20]
    assert enriched["act_day_part"].tolist() == ["Morning", "Evening"]


def test_calculate_session_duration_minutes():
    """Test duration calculation from session start and end timestamps."""
    df = pd.DataFrame({
        "session_start": ["2026-08-01 10:00:00", "2026-08-01 14:00:00"],
        "session_end": ["2026-08-01 10:45:00", "2026-08-01 15:30:00"]
    })
    res = calculate_session_duration_minutes(df)

    assert "duration_minutes" in res.columns
    assert res["duration_minutes"].tolist() == [45.0, 90.0]


def test_transform_entity_datetimes_sessions():
    """Test full sessions entity datetime transformation."""
    df = pd.DataFrame({
        "session_id": ["SES01", "SES02"],
        "student_id": ["S001", "S002"],
        "course_id": ["C101", "C101"],
        "session_start": ["2026-08-01 10:00:00", "2026-08-02 21:00:00"],
        "session_end": ["2026-08-01 11:00:00", "2026-08-02 22:30:00"]
    })
    res = transform_entity_datetimes(df, entity_name="sessions")

    assert "session_date" in res.columns
    assert "session_hour" in res.columns
    assert "session_day_part" in res.columns
    assert "session_is_weekend" in res.columns
    assert res["session_hour"].tolist() == [10, 21]
    assert res["session_day_part"].tolist() == ["Morning", "Evening"]
    assert res["duration_minutes"].tolist() == [60.0, 90.0]


def test_transform_all_datetimes():
    """Test batch transformation across all entity datasets."""
    datasets = {
        "students": pd.DataFrame({"registration_date": ["2026-01-15"]}),
        "quizzes": pd.DataFrame({"attempt_date": ["2026-02-10"]})
    }
    transformed = transform_all_datetimes(datasets)

    assert "reg_year" in transformed["students"].columns
    assert "quiz_week" in transformed["quizzes"].columns

"""
Date & Time Transformation Pipeline Module for Learning Analytics.
Extracts temporal features, handles timezones, derives learning habit indicators
(time of day, weekend study, hour-of-day, week number, cohort tenure) for behavioural modeling.
"""

from typing import Dict, Any, List, Optional, Union
import numpy as np
import pandas as pd
from src.utils import setup_logger, timed_step

logger = setup_logger(__name__)


def categorize_day_part(hour: Union[int, float]) -> str:
    """
    Categorizes the hour of day into behavioral study time buckets:
    - Night: 22:00 - 05:59
    - Morning: 06:00 - 11:59
    - Afternoon: 12:00 - 16:59
    - Evening: 17:00 - 21:59
    """
    if pd.isna(hour) or hour is None:
        return "Unknown"
    h = int(hour)
    if 6 <= h < 12:
        return "Morning"
    elif 12 <= h < 17:
        return "Afternoon"
    elif 17 <= h < 22:
        return "Evening"
    else:
        return "Night"


def parse_datetime_series(
    series: pd.Series,
    strip_timezone: bool = True
) -> pd.Series:
    """
    Robustly parses a timestamp Series into timezone-naive datetime64[ns].
    Handles multiple date formats, ISO-8601 with 'Z'/'UTC', and corrupt entries gracefully.
    """
    if series.empty:
        return series

    # Parse with pandas coerce
    dt_series = pd.to_datetime(series, errors="coerce", utc=True)
    
    if strip_timezone:
        # Convert to naive UTC timestamps suitable for SQL and downstream math
        dt_series = dt_series.dt.tz_localize(None)

    return dt_series


@timed_step("Extract Datetime Features")
def extract_datetime_features(
    df: pd.DataFrame,
    timestamp_column: str,
    prefix: str = "",
    include_time: bool = True
) -> pd.DataFrame:
    """
    Derives standard time-series and behavioral features from a timestamp column.
    
    Features extracted:
    - {prefix}date: 'YYYY-MM-DD' ISO date
    - {prefix}year: Year integer (e.g., 2026)
    - {prefix}month: Month integer (1-12)
    - {prefix}month_name: Full month string (e.g., 'January')
    - {prefix}day: Day of month (1-31)
    - {prefix}weekday: Day of week index (0=Monday, 6=Sunday)
    - {prefix}weekday_name: Full day string (e.g., 'Monday')
    - {prefix}is_weekend: Binary flag (1 if Saturday/Sunday else 0)
    - {prefix}week: ISO week number (1-53)
    - {prefix}week_number: Alias for week
    - {prefix}hour: Hour of day (0-23, if include_time=True)
    - {prefix}day_part: 'Morning', 'Afternoon', 'Evening', 'Night' (if include_time=True)
    """
    if df is None or df.empty or timestamp_column not in df.columns:
        return pd.DataFrame() if df is None else df

    enriched = df.copy()
    ts = parse_datetime_series(enriched[timestamp_column])
    
    # Store standard datetime64
    enriched[timestamp_column] = ts

    # Basic Date Components
    enriched[f"{prefix}date"] = ts.dt.strftime("%Y-%m-%d")
    enriched[f"{prefix}year"] = ts.dt.year.fillna(2026).astype(int)
    enriched[f"{prefix}month"] = ts.dt.month.fillna(1).astype(int)
    enriched[f"{prefix}month_name"] = ts.dt.month_name().fillna("Unknown")
    enriched[f"{prefix}day"] = ts.dt.day.fillna(1).astype(int)
    enriched[f"{prefix}weekday"] = ts.dt.weekday.fillna(0).astype(int)
    enriched[f"{prefix}weekday_name"] = ts.dt.day_name().fillna("Unknown")
    enriched[f"{prefix}is_weekend"] = enriched[f"{prefix}weekday"].apply(lambda w: 1 if w in (5, 6) else 0)
    
    # ISO Week Features
    iso_week = ts.dt.isocalendar().week.fillna(1).astype(int)
    enriched[f"{prefix}week"] = iso_week
    enriched[f"{prefix}week_number"] = iso_week

    # Time Components
    if include_time:
        enriched[f"{prefix}hour"] = ts.dt.hour.fillna(12).astype(int)
        enriched[f"{prefix}day_part"] = enriched[f"{prefix}hour"].apply(categorize_day_part)

    logger.info(
        f"Extracted {10 if not include_time else 12} datetime features from column '{timestamp_column}'"
    )
    return enriched


def calculate_session_duration_minutes(
    df: pd.DataFrame,
    start_col: str = "session_start",
    end_col: str = "session_end",
    duration_col: str = "duration_minutes"
) -> pd.DataFrame:
    """
    Calculates elapsed duration in minutes between two timestamps.
    """
    if df is None or df.empty or start_col not in df.columns or end_col not in df.columns:
        return df

    enriched = df.copy()
    start_dt = parse_datetime_series(enriched[start_col])
    end_dt = parse_datetime_series(enriched[end_col])

    diff_minutes = (end_dt - start_dt).dt.total_seconds() / 60.0
    # Replace negative or NaN values with existing duration or 0
    if duration_col in enriched.columns:
        enriched[duration_col] = np.where(diff_minutes > 0, diff_minutes.round(2), enriched[duration_col])
    else:
        enriched[duration_col] = diff_minutes.clip(lower=0.0).round(2).fillna(0.0)

    return enriched


@timed_step("Transform Entity Datetime Pipeline")
def transform_entity_datetimes(
    df: pd.DataFrame,
    entity_name: str
) -> pd.DataFrame:
    """
    Applies entity-specific date & time transformations.
    """
    if df is None or df.empty:
        return pd.DataFrame() if df is None else df

    enriched = df.copy()
    ent = entity_name.lower().strip()

    if ent == "sessions":
        if "session_start" in enriched.columns:
            enriched = extract_datetime_features(
                enriched,
                timestamp_column="session_start",
                prefix="session_",
                include_time=True
            )
            # Create root alias session_date
            if "session_date" not in enriched.columns and "session_session_date" in enriched.columns:
                enriched["session_date"] = enriched["session_session_date"]
            elif "session_date" not in enriched.columns:
                enriched["session_date"] = enriched["session_date"]
                
        if "session_start" in enriched.columns and "session_end" in enriched.columns:
            enriched = calculate_session_duration_minutes(
                enriched,
                start_col="session_start",
                end_col="session_end",
                duration_col="duration_minutes"
            )

    elif ent == "students":
        if "registration_date" in enriched.columns:
            enriched = extract_datetime_features(
                enriched,
                timestamp_column="registration_date",
                prefix="reg_",
                include_time=False
            )

    elif ent == "quizzes":
        if "attempt_date" in enriched.columns:
            enriched = extract_datetime_features(
                enriched,
                timestamp_column="attempt_date",
                prefix="quiz_",
                include_time=False
            )

    return enriched


def transform_all_datetimes(
    datasets: Dict[str, pd.DataFrame]
) -> Dict[str, pd.DataFrame]:
    """
    Transforms datetime columns across all project datasets.
    """
    transformed = {}
    for name, df in datasets.items():
        transformed[name] = transform_entity_datetimes(df, entity_name=name)
    return transformed

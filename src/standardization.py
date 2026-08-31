"""
Data Type Enforcement & Standardisation Module for Learning Analytics.
Provides robust parsers and transformers to standardize IDs, timestamps,
numerical metrics, percentage strings, categorical domains, and boolean flags for SQL analytics.
"""

import re
from typing import Dict, Any, List, Optional, Union, Tuple
import numpy as np
import pandas as pd
from src.utils import setup_logger, timed_step, TransformationError

logger = setup_logger(__name__)

# Standard Category Mappings for Platform Entities
CATEGORY_MAPPINGS: Dict[str, Dict[str, str]] = {
    "completion_status": {
        "completed": "Completed",
        "complete": "Completed",
        "finished": "Completed",
        "passed": "Completed",
        "graduated": "Completed",
        "in progress": "In Progress",
        "in-progress": "In Progress",
        "ongoing": "In Progress",
        "active": "In Progress",
        "dropped": "Dropped",
        "dropout": "Dropped",
        "drop": "Dropped",
        "quit": "Dropped",
        "withdrawn": "Dropped",
        "inactive": "Inactive",
        "dormant": "Inactive",
        "unknown": "Unknown"
    },
    "gender": {
        "m": "Male",
        "male": "Male",
        "man": "Male",
        "f": "Female",
        "female": "Female",
        "woman": "Female",
        "non-binary": "Non-Binary",
        "nonbinary": "Non-Binary",
        "nb": "Non-Binary",
        "other": "Other",
        "prefer not to say": "Prefer not to say",
        "unknown": "Unknown"
    },
    "device_type": {
        "desktop": "Desktop",
        "pc": "Desktop",
        "laptop": "Laptop",
        "notebook": "Laptop",
        "macbook": "Laptop",
        "mobile": "Mobile",
        "phone": "Mobile",
        "smartphone": "Mobile",
        "android": "Mobile",
        "ios": "Mobile",
        "iphone": "Mobile",
        "tablet": "Tablet",
        "ipad": "Tablet",
        "unknown": "Unknown"
    },
    "education_level": {
        "high school": "High School",
        "highschool": "High School",
        "secondary": "High School",
        "12th": "High School",
        "undergraduate": "Undergraduate",
        "undergrad": "Undergraduate",
        "bachelors": "Undergraduate",
        "bachelor": "Undergraduate",
        "bs": "Undergraduate",
        "ba": "Undergraduate",
        "btech": "Undergraduate",
        "postgraduate": "Postgraduate",
        "postgrad": "Postgraduate",
        "masters": "Postgraduate",
        "master": "Postgraduate",
        "ms": "Postgraduate",
        "ma": "Postgraduate",
        "mtech": "Postgraduate",
        "doctorate": "Doctorate",
        "doctoral": "Doctorate",
        "phd": "Doctorate",
        "other": "Other",
        "unknown": "Unknown"
    }
}


def clean_percentage_value(val: Any) -> Optional[float]:
    """
    Parses messy percentage representations ('85%', ' 92.5 % ', 0.85, '85') into standard 0-100 float.
    """
    if pd.isna(val) or val is None or val == "":
        return None
    
    if isinstance(val, (int, float)):
        # If expressed as fraction <= 1.0 (e.g., 0.85) when non-zero, convert to percentage
        if 0.0 < val <= 1.0:
            return round(val * 100.0, 2)
        return round(float(val), 2)

    val_str = str(val).strip().replace("%", "").replace(",", "")
    try:
        float_val = float(val_str)
        if 0.0 < float_val <= 1.0:
            return round(float_val * 100.0, 2)
        return round(float_val, 2)
    except ValueError:
        logger.warning(f"Could not parse percentage value: '{val}'")
        return None


def clean_boolean_flag(val: Any) -> int:
    """
    Normalizes diverse boolean inputs (True, 'true', '1', 'PASS', 'yes') into integer flag 1 or 0.
    """
    if pd.isna(val) or val is None:
        return 0

    if isinstance(val, bool):
        return 1 if val else 0

    if isinstance(val, (int, float)):
        return 1 if val != 0 else 0

    val_clean = str(val).strip().lower()
    truthy = {"1", "true", "t", "yes", "y", "pass", "passed", "completed", "success"}
    return 1 if val_clean in truthy else 0


def standardize_identifiers(df: pd.DataFrame, id_columns: List[str]) -> pd.DataFrame:
    """
    Enforces uppercase, stripped formatting on ID columns.
    """
    transformed = df.copy()
    for col in id_columns:
        if col in transformed.columns:
            transformed[col] = transformed[col].astype(str).str.strip().str.upper()
            # Replace 'NAN' / 'NONE' / 'NULL' string artifacts with clean string or NA
            transformed[col] = transformed[col].replace({"NAN": "UNKNOWN", "NONE": "UNKNOWN", "NULL": "UNKNOWN"})
    return transformed


def standardize_dates(
    df: pd.DataFrame,
    date_columns: List[str],
    as_iso_string: bool = False
) -> pd.DataFrame:
    """
    Parses dates into datetime64 or standardized ISO string format (YYYY-MM-DD).
    """
    transformed = df.copy()
    for col in date_columns:
        if col in transformed.columns:
            transformed[col] = pd.to_datetime(transformed[col], errors="coerce")
            if as_iso_string:
                transformed[col] = transformed[col].dt.strftime("%Y-%m-%d").fillna("")
    return transformed


def standardize_timestamps(
    df: pd.DataFrame,
    timestamp_columns: List[str],
    as_iso_string: bool = False
) -> pd.DataFrame:
    """
    Parses timestamps into datetime64 or standardized ISO string (YYYY-MM-DD HH:MM:SS).
    """
    transformed = df.copy()
    for col in timestamp_columns:
        if col in transformed.columns:
            transformed[col] = pd.to_datetime(transformed[col], errors="coerce")
            if as_iso_string:
                transformed[col] = transformed[col].dt.strftime("%Y-%m-%d %H:%M:%S").fillna("")
    return transformed


def standardize_categories(
    df: pd.DataFrame,
    category_columns: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Normalizes categorical fields using project standard synonym mapping dictionaries.
    """
    transformed = df.copy()
    target_cols = category_columns or list(CATEGORY_MAPPINGS.keys())

    for col in target_cols:
        if col in transformed.columns and col in CATEGORY_MAPPINGS:
            mapping = CATEGORY_MAPPINGS[col]
            
            def map_val(x):
                if pd.isna(x) or x is None:
                    return "Unknown"
                clean_k = str(x).strip().lower()
                return mapping.get(clean_k, str(x).strip().title())

            transformed[col] = transformed[col].apply(map_val)

    return transformed


@timed_step("Standardize Entity Data Types")
def standardize_entity(
    df: pd.DataFrame,
    entity_name: str,
    as_sql_types: bool = False
) -> pd.DataFrame:
    """
    Applies comprehensive data type enforcement and value standardization to a specific entity.
    """
    if df is None or df.empty:
        return pd.DataFrame() if df is None else df

    cleaned = df.copy()
    ent = entity_name.lower().strip()

    if ent == "students":
        cleaned = standardize_identifiers(cleaned, ["student_id", "target_course_id"])
        cleaned = standardize_dates(cleaned, ["registration_date", "completion_date"], as_iso_string=as_sql_types)
        cleaned = standardize_categories(cleaned, ["gender", "education_level", "device_type", "completion_status"])
        if "age" in cleaned.columns:
            cleaned["age"] = pd.to_numeric(cleaned["age"], errors="coerce").fillna(24).astype(int)

    elif ent == "courses":
        cleaned = standardize_identifiers(cleaned, ["course_id"])
        if "category" in cleaned.columns:
            cleaned["category"] = cleaned["category"].astype(str).str.strip().str.title()
        if "total_modules" in cleaned.columns:
            cleaned["total_modules"] = pd.to_numeric(cleaned["total_modules"], errors="coerce").fillna(10).astype(int)
        if "total_quizzes" in cleaned.columns:
            cleaned["total_quizzes"] = pd.to_numeric(cleaned["total_quizzes"], errors="coerce").fillna(4).astype(int)
        if "estimated_duration_hours" in cleaned.columns:
            cleaned["estimated_duration_hours"] = pd.to_numeric(cleaned["estimated_duration_hours"], errors="coerce").astype(float)

    elif ent == "sessions":
        cleaned = standardize_identifiers(cleaned, ["session_id", "student_id", "course_id"])
        cleaned = standardize_timestamps(cleaned, ["session_start", "session_end"], as_iso_string=as_sql_types)
        for num_col in ["duration_minutes", "active_minutes", "idle_minutes", "video_watched_minutes", "reading_minutes"]:
            if num_col in cleaned.columns:
                cleaned[num_col] = pd.to_numeric(cleaned[num_col], errors="coerce").fillna(0.0).astype(float)
        if "modules_accessed" in cleaned.columns:
            cleaned["modules_accessed"] = pd.to_numeric(cleaned["modules_accessed"], errors="coerce").fillna(0).astype(int)

    elif ent == "quizzes":
        cleaned = standardize_identifiers(cleaned, ["quiz_attempt_id", "student_id", "course_id", "quiz_id"])
        cleaned = standardize_dates(cleaned, ["attempt_date"], as_iso_string=as_sql_types)
        if "score_percentage" in cleaned.columns:
            cleaned["score_percentage"] = cleaned["score_percentage"].apply(clean_percentage_value)
            cleaned["score_percentage"] = pd.to_numeric(cleaned["score_percentage"], errors="coerce").fillna(75.0).astype(float)
        if "attempt_number" in cleaned.columns:
            cleaned["attempt_number"] = pd.to_numeric(cleaned["attempt_number"], errors="coerce").fillna(1).astype(int)
        if "time_taken_minutes" in cleaned.columns:
            cleaned["time_taken_minutes"] = pd.to_numeric(cleaned["time_taken_minutes"], errors="coerce").fillna(15.0).astype(float)
        if "passed" in cleaned.columns:
            cleaned["passed"] = cleaned["passed"].apply(clean_boolean_flag).astype(int)

    logger.info(f"Standardized data types and values for entity '{entity_name}' ({len(cleaned)} rows)")
    return cleaned

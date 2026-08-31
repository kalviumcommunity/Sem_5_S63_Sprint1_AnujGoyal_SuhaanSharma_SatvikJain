"""
Data Transformation Foundations Module for Learning Analytics.
Provides reusable functions to clean column names, cast data types, parse timestamps, and apply basic derivations.
"""

import re
from typing import Dict, List, Callable, Any, Optional
import pandas as pd
import numpy as np
from src.utils import setup_logger, timed_step, TransformationError

logger = setup_logger(__name__)


@timed_step("Standardize Column Names")
def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardizes DataFrame column names:
    - Strips leading/trailing whitespace
    - Converts to lowercase
    - Replaces spaces, dashes, and special characters with underscores
    - Removes consecutive underscores
    """
    if df.empty:
        return df
    
    transformed = df.copy()
    new_columns = []
    for col in transformed.columns:
        clean_col = str(col).strip().lower()
        clean_col = re.sub(r"[^\w\s]", "_", clean_col)
        clean_col = re.sub(r"\s+", "_", clean_col)
        clean_col = re.sub(r"_+", "_", clean_col)
        clean_col = clean_col.strip("_")
        new_columns.append(clean_col)
    
    transformed.columns = new_columns
    logger.info(f"Standardized {len(new_columns)} column names.")
    return transformed


@timed_step("Cast Column Types")
def cast_column_types(df: pd.DataFrame, type_mapping: Dict[str, str]) -> pd.DataFrame:
    """
    Casts DataFrame columns to specified types with error handling.
    """
    if df.empty or not type_mapping:
        return df

    transformed = df.copy()
    for col, target_type in type_mapping.items():
        if col in transformed.columns:
            try:
                if target_type in ("int", "int64", "integer"):
                    transformed[col] = pd.to_numeric(transformed[col], errors="coerce").fillna(0).astype(int)
                elif target_type in ("float", "float64", "real"):
                    transformed[col] = pd.to_numeric(transformed[col], errors="coerce").astype(float)
                elif target_type in ("str", "string", "object"):
                    transformed[col] = transformed[col].astype(str)
                elif target_type in ("bool", "boolean"):
                    transformed[col] = transformed[col].astype(bool)
                else:
                    transformed[col] = transformed[col].astype(target_type)
            except Exception as e:
                raise TransformationError(f"Failed to cast column '{col}' to '{target_type}': {e}") from e
    return transformed


@timed_step("Parse Datetime Columns")
def parse_datetime_columns(
    df: pd.DataFrame,
    columns: List[str],
    date_format: Optional[str] = None
) -> pd.DataFrame:
    """
    Parses string date columns into pandas datetime objects with 'coerce' error handling.
    """
    if df.empty or not columns:
        return df

    transformed = df.copy()
    for col in columns:
        if col in transformed.columns:
            try:
                transformed[col] = pd.to_datetime(transformed[col], format=date_format, errors="coerce")
                logger.info(f"Parsed datetime column: '{col}'")
            except Exception as e:
                raise TransformationError(f"Failed to parse datetime column '{col}': {e}") from e
    return transformed


def derive_column(
    df: pd.DataFrame,
    new_column_name: str,
    calculation_func: Callable[[pd.DataFrame], pd.Series]
) -> pd.DataFrame:
    """
    Derives a new column using a provided calculation function.
    """
    if df.empty:
        return df

    transformed = df.copy()
    try:
        transformed[new_column_name] = calculation_func(transformed)
        logger.info(f"Derived new column: '{new_column_name}'")
        return transformed
    except Exception as e:
        raise TransformationError(f"Failed to derive column '{new_column_name}': {e}") from e

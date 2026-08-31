"""
Data Cleaning Module for Learning Analytics.
Handles deduplication, missing value imputation, type casting, and standardisation.
"""

import pandas as pd
from src.utils import setup_logger

logger = setup_logger(__name__)


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Performs baseline cleaning on a DataFrame."""
    if df.empty:
        return df
    
    cleaned = df.drop_duplicates().copy()
    # Strip whitespace from string and object columns
    str_cols = cleaned.select_dtypes(include=["object", "string"]).columns
    for col in str_cols:
        cleaned[col] = cleaned[col].astype(str).str.strip()
        
    logger.info(f"Cleaned dataset: {len(df)} -> {len(cleaned)} rows")
    return cleaned

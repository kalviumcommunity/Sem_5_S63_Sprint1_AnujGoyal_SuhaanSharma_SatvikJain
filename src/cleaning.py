"""
Data Cleaning Module for Learning Analytics.
Handles deduplication, missing value imputation, data type enforcement, and value standardisation.
"""

from typing import Dict, Any, Tuple, Optional
import pandas as pd
from src.utils import setup_logger
from src.imputation import (
    detect_missing_values,
    impute_dataset,
    impute_all_datasets,
    ImputationReport
)
from src.standardization import (
    standardize_entity,
    clean_percentage_value,
    clean_boolean_flag,
    standardize_categories,
    standardize_identifiers,
    standardize_dates,
    standardize_timestamps
)

logger = setup_logger(__name__)


def clean_dataframe(
    df: pd.DataFrame,
    entity_name: Optional[str] = None,
    impute_nulls: bool = True,
    standardize: bool = True
) -> pd.DataFrame:
    """
    Performs comprehensive cleaning on a DataFrame:
    1. Deduplication
    2. String whitespace stripping
    3. Domain-specific missing value imputation
    4. Type enforcement and category/date/boolean standardisation
    """
    if df is None or df.empty:
        return pd.DataFrame() if df is None else df
    
    cleaned = df.drop_duplicates().copy()

    # Strip whitespace from string and object columns
    str_cols = cleaned.select_dtypes(include=["object", "string"]).columns
    for col in str_cols:
        cleaned[col] = cleaned[col].astype(str).str.strip()

    # Domain imputation
    if impute_nulls:
        cleaned, _ = impute_dataset(cleaned, entity_name=entity_name)

    # Standardization
    if standardize and entity_name:
        cleaned = standardize_entity(cleaned, entity_name=entity_name)

    logger.info(f"Cleaned dataset: {len(df)} -> {len(cleaned)} rows")
    return cleaned

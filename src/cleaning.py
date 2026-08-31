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
from src.deduplication import (
    detect_duplicates,
    deduplicate_dataset,
    deduplicate_all_datasets,
    generate_deduplication_scorecard,
    DeduplicationReport
)

logger = setup_logger(__name__)


def clean_dataframe(
    df: pd.DataFrame,
    entity_name: Optional[str] = None,
    deduplicate: bool = True,
    impute_nulls: bool = True,
    standardize: bool = True
) -> pd.DataFrame:
    """
    Performs comprehensive multi-stage cleaning on a DataFrame:
    1. Exact & Business-Key Deduplication
    2. String whitespace stripping
    3. Domain-specific missing value imputation
    4. Type enforcement and category/date/boolean standardisation
    """
    if df is None or df.empty:
        return pd.DataFrame() if df is None else df
    
    cleaned = df.copy()

    # 1. Deduplication
    if deduplicate:
        cleaned, _ = deduplicate_dataset(cleaned, entity_name=entity_name)

    # 2. Strip whitespace from string and object columns
    str_cols = cleaned.select_dtypes(include=["object", "string"]).columns
    for col in str_cols:
        cleaned[col] = cleaned[col].astype(str).str.strip()

    # 3. Domain imputation
    if impute_nulls:
        cleaned, _ = impute_dataset(cleaned, entity_name=entity_name)

    # 4. Standardization
    if standardize and entity_name:
        cleaned = standardize_entity(cleaned, entity_name=entity_name)

    logger.info(f"Cleaned dataset '{entity_name or 'generic'}': {len(df)} -> {len(cleaned)} rows")
    return cleaned

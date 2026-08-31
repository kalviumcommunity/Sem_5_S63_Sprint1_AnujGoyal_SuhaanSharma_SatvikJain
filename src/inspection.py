"""
Dataset Inspection & Profiling Module for Learning Analytics.
Provides reusable functions to inspect data structures, types, missingness, and memory.
"""

from typing import Dict, Any, Optional
import pandas as pd
from src.utils import setup_logger, timed_step

logger = setup_logger(__name__)


@timed_step("Inspect DataFrame")
def inspect_dataframe(df: pd.DataFrame, dataset_name: str = "Dataset") -> Dict[str, Any]:
    """
    Performs comprehensive structural inspection of a DataFrame.
    Returns metadata including shape, columns, dtypes, null counts, duplicate rows, and memory usage.
    """
    if df.empty:
        logger.warning(f"Inspection requested on empty DataFrame: '{dataset_name}'")
        return {
            "dataset_name": dataset_name,
            "status": "EMPTY",
            "row_count": 0,
            "column_count": 0,
            "columns": [],
            "dtypes": {},
            "null_counts": {},
            "null_percentages": {},
            "duplicate_rows": 0,
            "memory_usage_mb": 0.0
        }

    total_rows = len(df)
    null_counts = df.isnull().sum().to_dict()
    null_percentages = {col: (count / total_rows) * 100.0 for col, count in null_counts.items()}
    memory_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
    duplicate_count = int(df.duplicated().sum())

    inspection = {
        "dataset_name": dataset_name,
        "status": "POPULATED",
        "row_count": total_rows,
        "column_count": len(df.columns),
        "columns": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "null_counts": null_counts,
        "null_percentages": null_percentages,
        "duplicate_rows": duplicate_count,
        "memory_usage_mb": round(memory_mb, 4)
    }

    logger.info(
        f"Inspected '{dataset_name}': {total_rows} rows, {len(df.columns)} cols, "
        f"{duplicate_count} duplicates, {memory_mb:.2f} MB"
    )
    return inspection


def get_column_summary(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """Generates column-level summaries including unique counts and sample values."""
    if df.empty:
        return {}
    
    summary = {}
    for col in df.columns:
        summary[col] = {
            "dtype": str(df[col].dtype),
            "unique_count": int(df[col].nunique(dropna=True)),
            "null_count": int(df[col].isnull().sum()),
            "sample_values": df[col].dropna().head(3).tolist()
        }
    return summary

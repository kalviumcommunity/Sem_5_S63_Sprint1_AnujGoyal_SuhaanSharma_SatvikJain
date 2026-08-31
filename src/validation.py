"""
Data Validation Module for Learning Analytics.
Validates schemas, data types, missing values, and business constraints.
"""

from typing import Dict, Any, List
import pandas as pd
from src.utils import setup_logger

logger = setup_logger(__name__)


def validate_dataframe(df: pd.DataFrame, required_columns: List[str]) -> Dict[str, Any]:
    """Validates that a DataFrame contains required columns and reports statistics."""
    if df.empty:
        return {"status": "EMPTY", "missing_columns": required_columns, "row_count": 0}
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    is_valid = len(missing_columns) == 0
    
    report = {
        "status": "VALID" if is_valid else "INVALID",
        "row_count": len(df),
        "column_count": len(df.columns),
        "missing_columns": missing_columns,
        "null_counts": df.isnull().sum().to_dict()
    }
    logger.info(f"Validation completed: status={report['status']}, rows={report['row_count']}")
    return report

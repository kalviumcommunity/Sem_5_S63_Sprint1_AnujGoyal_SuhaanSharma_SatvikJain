"""
Statistical Analysis and EDA Module for Learning Analytics.
"""

from typing import Dict, Any
import pandas as pd
from src.utils import setup_logger

logger = setup_logger(__name__)


def generate_summary_statistics(df: pd.DataFrame) -> Dict[str, Any]:
    """Generates numerical and categorical summary statistics."""
    if df.empty:
        return {}
    return {
        "numeric_summary": df.describe().to_dict(),
        "shape": df.shape,
        "dtypes": df.dtypes.astype(str).to_dict()
    }

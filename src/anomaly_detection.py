"""
Anomaly Detection & Risk Scoring Module for Learning Analytics.
Identifies outlier learning behaviours and students at risk of silent dropout.
"""

from typing import List
import pandas as pd
from src.utils import setup_logger

logger = setup_logger(__name__)


def detect_outliers_iqr(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Identifies outliers in a numeric column using the IQR method."""
    if df.empty or column not in df.columns:
        return pd.DataFrame()
    
    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    
    outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
    logger.info(f"Detected {len(outliers)} outliers in column {column}")
    return outliers

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


def get_business_kpis(db_path: Any = None) -> Dict[str, Any]:
    """
    Retrieves core executive KPIs and business metrics from SQLite analytics layer.
    """
    from src.database import execute_business_metrics

    metrics_result = execute_business_metrics(db_path=db_path)
    return metrics_result.get("kpis", {})



def run_multi_table_join_analysis(db_path: Any = None) -> Dict[str, pd.DataFrame]:
    """
    Executes multi-table INNER and LEFT JOIN queries combining students, courses, sessions, quizzes, and features.
    """
    from src.database import execute_multi_table_joins

    return execute_multi_table_joins(db_path=db_path)

def run_aggregation_analysis(db_path: Any = None) -> Dict[str, pd.DataFrame]:
    """
    Executes SQL filtering, grouping, and aggregation queries for deep cohort analysis.
    """
    from src.database import execute_aggregation_queries

    return execute_aggregation_queries(db_path=db_path)




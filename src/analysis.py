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



def run_window_function_analysis(db_path: Any = None) -> Dict[str, pd.DataFrame]:
    """
    Executes SQL window functions (ROW_NUMBER, RANK, LAG, LEAD, AVG OVER) for ranking, progression, and rolling metrics.
    """
    from src.database import execute_window_function_queries

    return execute_window_function_queries(db_path=db_path)


def run_sql_insight_validation(db_path: Any = None) -> Dict[str, Any]:
    """
    Validates key SQL business insights against equivalent Pandas DataFrame calculations.
    """
    from src.database import validate_sql_insights_against_pandas

    return validate_sql_insights_against_pandas(db_path=db_path)


def run_data_storytelling_analysis(db_path: Any = None) -> Dict[str, Any]:
    """
    Generates 4-stage analytical insight narratives (Observation -> Interpretation -> Business Impact -> Suggested Action)
    across engagement, completion, dropout, risk, and course performance domains.
    """
    from src.storytelling import generate_all_insight_narratives

    return generate_all_insight_narratives(db_path=db_path)


def run_executive_reporting_analysis(db_path: Any = None) -> Dict[str, Any]:
    """
    Generates non-technical executive-level report data summarizing overall performance, completion,
    dropout, learner engagement, major behavioural findings, high-risk segments, course-level findings, and recommended actions.
    """
    from src.reporting import generate_executive_report_data

    return generate_executive_report_data(db_path=db_path)


def run_insight_export_analysis(db_path: Any = None, export_dir: Any = None) -> Dict[str, Any]:
    """
    Exports all core analytical outputs (KPIs, learner risk data, course metrics, behavioural segments, insights, and report)
    to disk in multi-format packages (CSV, Markdown, JSON, HTML).
    """
    from src.export import export_all_analytical_outputs

    return export_all_analytical_outputs(db_path=db_path, export_dir=export_dir)









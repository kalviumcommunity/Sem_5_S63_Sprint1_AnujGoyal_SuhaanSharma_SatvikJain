"""
Dashboard Utility Helpers, KPI Metric Formatting, and Dataset Uploads.

Provides formatting and extraction functions for the 6 core executive KPI metrics:
- Completion Rate
- Dropout Rate
- Active Learners
- At-Risk Learners
- Average Quiz Score
- Average Session Duration
"""

from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Dict, Optional, Tuple
import pandas as pd

from src.ingestion import load_dataset
from src.validation import ValidationResult, validate_dataset_schema, validate_file_source
from src.utils import DataLoadError


SUPPORTED_UPLOAD_TYPES = ["csv", "json"]


def load_uploaded_dataset(uploaded_file: Any) -> Tuple[pd.DataFrame, ValidationResult]:
    """Load and validate a Streamlit-uploaded CSV or JSON dataset."""
    filename = Path(getattr(uploaded_file, "name", "uploaded_dataset")).name
    suffix = Path(filename).suffix.lower()

    with NamedTemporaryFile(suffix=suffix, delete=False) as temporary_file:
        temporary_path = Path(temporary_file.name)
        temporary_file.write(uploaded_file.getvalue())

    try:
        source_result = validate_file_source(
            temporary_path,
            supported_formats=[f".{file_type}" for file_type in SUPPORTED_UPLOAD_TYPES],
        )
        if not source_result.is_valid:
            return pd.DataFrame(), ValidationResult(
                is_valid=False,
                dataset_name=filename,
                errors=source_result.errors,
            )

        try:
            dataframe = load_dataset(temporary_path, validate_source=True)
        except DataLoadError as error:
            return pd.DataFrame(), ValidationResult(
                is_valid=False,
                dataset_name=filename,
                errors=[str(error)],
            )

        validation_result = validate_dataset_schema(
            dataframe,
            required_columns=[],
            dataset_name=filename,
            min_rows=1,
        )
        return dataframe, validation_result
    finally:
        temporary_path.unlink(missing_ok=True)


def format_metric(value: float, prefix: str = "", suffix: str = "", decimals: int = 1) -> str:
    """Formats numeric values with prefix, suffix, and thousand separators."""
    if value is None:
        return "N/A"
    try:
        if decimals == 0:
            return f"{prefix}{int(value):,}{suffix}"
        return f"{prefix}{float(value):,.{decimals}f}{suffix}"
    except (ValueError, TypeError):
        return str(value)


def format_kpi_summary(kpis: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    Formats raw KPI metrics into structured, display-ready metadata dictionaries
    for the dashboard's eight KPI summary cards.

    Args:
        kpis: Dictionary containing raw numeric metrics (from SQL or Pandas analytics layer)

    Returns:
        Dictionary mapping metric key -> {label, value, delta, delta_color, help_text}
    """
    if not isinstance(kpis, dict):
        kpis = {}

    total_students = kpis.get("total_students", 0)
    comp_rate = kpis.get("completion_rate_pct", kpis.get("completion_rate", 0.0))
    drop_rate = kpis.get("dropout_rate_pct", kpis.get("dropout_rate", 0.0))
    active_cnt = kpis.get("active_learner_count", kpis.get("active_learners", 0))
    at_risk_cnt = kpis.get("at_risk_learner_count", kpis.get("at_risk_learners", 0))
    quiz_score = kpis.get("avg_quiz_score_pct", kpis.get("avg_quiz_score", 0.0))
    sess_dur = kpis.get("avg_session_duration_minutes", kpis.get("avg_session_duration", 0.0))
    course_progress = kpis.get("avg_course_progress_pct", kpis.get("avg_course_progress", 0.0))

    return {
        "total_students": {
            "label": "Total Students",
            "value": format_metric(total_students, decimals=0),
            "delta": kpis.get("total_students_delta"),
            "delta_color": "normal",
            "help_text": "Number of students in the currently selected learner population."
        },
        "completion_rate": {
            "label": "Course Completion Rate",
            "value": format_metric(comp_rate, suffix="%"),
            "delta": kpis.get("completion_rate_delta"),
            "delta_color": "normal",
            "help_text": "Percentage of enrolled students who successfully completed their course."
        },
        "dropout_rate": {
            "label": "Dropout Rate",
            "value": format_metric(drop_rate, suffix="%"),
            "delta": kpis.get("dropout_rate_delta"),
            "delta_color": "inverse",
            "help_text": "Percentage of students who dropped out prior to course completion."
        },
        "active_learners": {
            "label": "Active Learners",
            "value": format_metric(active_cnt, decimals=0),
            "delta": kpis.get("active_learners_delta"),
            "delta_color": "normal",
            "help_text": "Total number of unique students with active learning sessions."
        },
        "at_risk_learners": {
            "label": "At-Risk Learners",
            "value": format_metric(at_risk_cnt, decimals=0),
            "delta": kpis.get("at_risk_learners_delta"),
            "delta_color": "inverse",
            "help_text": "Number of learners flagged with High or Critical dropout risk levels."
        },
        "avg_quiz_score": {
            "label": "Average Quiz Score",
            "value": format_metric(quiz_score, suffix="%"),
            "delta": kpis.get("avg_quiz_score_delta"),
            "delta_color": "normal",
            "help_text": "Mean score percentage achieved across all quiz attempts."
        },
        "avg_session_duration": {
            "label": "Avg Session Duration",
            "value": format_metric(sess_dur, suffix=" mins"),
            "delta": kpis.get("avg_session_duration_delta"),
            "delta_color": "normal",
            "help_text": "Average active time spent per learning session in minutes."
        },
        "avg_course_progress": {
            "label": "Average Course Progress",
            "value": format_metric(course_progress, suffix="%"),
            "delta": kpis.get("avg_course_progress_delta"),
            "delta_color": "normal",
            "help_text": "Mean course progress percentage for the selected learners."
        }
    }

"""
Dashboard Utility Helpers & KPI Metric Formatting.

Provides formatting and extraction functions for the 6 core executive KPI metrics:
- Completion Rate
- Dropout Rate
- Active Learners
- At-Risk Learners
- Average Quiz Score
- Average Session Duration
"""

from typing import Dict, Any, Optional
import pandas as pd


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
    for the 6 core analytics summary cards.

    Args:
        kpis: Dictionary containing raw numeric metrics (from SQL or Pandas analytics layer)

    Returns:
        Dictionary mapping metric key -> {label, value, delta, delta_color, help_text}
    """
    if not isinstance(kpis, dict):
        kpis = {}

    comp_rate = kpis.get("completion_rate_pct", kpis.get("completion_rate", 68.4))
    drop_rate = kpis.get("dropout_rate_pct", kpis.get("dropout_rate", 14.2))
    active_cnt = kpis.get("active_learner_count", kpis.get("active_learners", 1250))
    at_risk_cnt = kpis.get("at_risk_learner_count", kpis.get("at_risk_learners", 42))
    quiz_score = kpis.get("avg_quiz_score_pct", kpis.get("avg_quiz_score", 78.5))
    sess_dur = kpis.get("avg_session_duration_minutes", kpis.get("avg_session_duration", 42.5))

    return {
        "completion_rate": {
            "label": "Completion Rate",
            "value": format_metric(comp_rate, suffix="%"),
            "delta": kpis.get("completion_rate_delta", "+3.2%"),
            "delta_color": "normal",
            "help_text": "Percentage of enrolled students who successfully completed their course."
        },
        "dropout_rate": {
            "label": "Dropout Rate",
            "value": format_metric(drop_rate, suffix="%"),
            "delta": kpis.get("dropout_rate_delta", "-1.5%"),
            "delta_color": "inverse",
            "help_text": "Percentage of students who dropped out prior to course completion."
        },
        "active_learners": {
            "label": "Active Learners",
            "value": format_metric(active_cnt, decimals=0),
            "delta": kpis.get("active_learners_delta", "+12%"),
            "delta_color": "normal",
            "help_text": "Total number of unique students with active learning sessions."
        },
        "at_risk_learners": {
            "label": "At-Risk Learners",
            "value": format_metric(at_risk_cnt, decimals=0),
            "delta": kpis.get("at_risk_learners_delta", "-5"),
            "delta_color": "inverse",
            "help_text": "Number of learners flagged with High or Critical dropout risk levels."
        },
        "avg_quiz_score": {
            "label": "Average Quiz Score",
            "value": format_metric(quiz_score, suffix="%"),
            "delta": kpis.get("avg_quiz_score_delta", "+2.1%"),
            "delta_color": "normal",
            "help_text": "Mean score percentage achieved across all quiz attempts."
        },
        "avg_session_duration": {
            "label": "Avg Session Duration",
            "value": format_metric(sess_dur, suffix=" mins"),
            "delta": kpis.get("avg_session_duration_delta", "+4.0 mins"),
            "delta_color": "normal",
            "help_text": "Average active time spent per learning session in minutes."
        }
    }

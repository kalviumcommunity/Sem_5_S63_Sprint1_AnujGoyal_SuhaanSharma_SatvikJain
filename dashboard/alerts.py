"""Reusable configurable threshold monitoring for learning analytics metrics."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import pandas as pd


NORMAL = "NORMAL"
WARNING = "WARNING"
CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class AlertThresholds:
    """Business thresholds used by the dashboard alert evaluator."""

    dropout_warning_pct: float = 20.0
    dropout_critical_pct: float = 35.0
    completion_warning_pct: float = 60.0
    completion_critical_pct: float = 40.0
    at_risk_warning_pct: float = 25.0
    at_risk_critical_pct: float = 40.0
    weekly_active_learners_warning: float = 100.0
    weekly_active_learners_critical: float = 50.0
    engagement_rate_warning_pct: float = 60.0
    engagement_rate_critical_pct: float = 40.0
    activity_decline_warning_pct: float = 10.0
    activity_decline_critical_pct: float = 25.0
    # Backward-compatible names used by existing dashboard integrations.
    engagement_decline_warning_pct: Optional[float] = None
    engagement_decline_critical_pct: Optional[float] = None


@dataclass(frozen=True)
class MetricAlert:
    """A business-readable result for one monitored metric."""

    metric: str
    status: str
    observed_value: float
    threshold: Optional[float]
    explanation: str
    data_available: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "metric": self.metric,
            "status": self.status,
            "observed_value": self.observed_value,
            "threshold": self.threshold,
            "explanation": self.explanation,
            "data_available": self.data_available,
        }


def _higher_is_worse(value: float, warning: float, critical: float) -> str:
    if value >= critical:
        return CRITICAL
    if value >= warning:
        return WARNING
    return NORMAL


def _lower_is_worse(value: float, warning: float, critical: float) -> str:
    if value <= critical:
        return CRITICAL
    if value <= warning:
        return WARNING
    return NORMAL


def _alert(
    metric: str,
    status: str,
    value: float,
    threshold: Optional[float],
    explanation: str,
    data_available: bool = True,
) -> MetricAlert:
    return MetricAlert(metric, status, round(float(value), 2), threshold, explanation, data_available)


def _threshold_explanation(
    status: str,
    value: float,
    normal_text: str,
    action_text: str,
) -> str:
    if status == NORMAL:
        return normal_text
    return f"{value:.1f}% {action_text}"


def _number(value: Any) -> Optional[float]:
    """Return a finite numeric value, preserving missing-data semantics."""
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    number = pd.to_numeric(value, errors="coerce")
    return float(number) if pd.notna(number) else None


def _threshold_for_status(status: str, warning: float, critical: float) -> float:
    return critical if status == CRITICAL else warning


def _minimum_alert(
    metric: str,
    value: Optional[float],
    warning: float,
    critical: float,
    label: str,
) -> MetricAlert:
    if value is None:
        return _alert(
            metric, NORMAL, 0.0, warning,
            f"Not enough data to evaluate {label}; no alert was raised.", False,
        )
    status = _lower_is_worse(value, warning, critical)
    threshold = _threshold_for_status(status, warning, critical)
    if status == NORMAL:
        explanation = f"{label} is {value:.1f}, at or above the minimum threshold of {warning:.1f}."
    else:
        explanation = f"{label} is {value:.1f}, below the {status.lower()} threshold of {threshold:.1f}."
    return _alert(metric, status, value, threshold, explanation)


def _percentage_alert(
    metric: str,
    value: Optional[float],
    warning: float,
    critical: float,
    label: str,
    higher_is_worse: bool,
) -> MetricAlert:
    if value is None:
        return _alert(
            metric, NORMAL, 0.0, warning,
            f"Not enough data to evaluate {label}; no alert was raised.", False,
        )
    status = (
        _higher_is_worse(value, warning, critical)
        if higher_is_worse
        else _lower_is_worse(value, warning, critical)
    )
    threshold = _threshold_for_status(status, warning, critical)
    if status == NORMAL:
        explanation = f"{label} is {value:.1f}%, within the acceptable range."
    else:
        action = "; retention intervention is needed" if metric == "Dropout Rate" else ""
        explanation = f"{label} is {value:.1f}%, crossing the {status.lower()} threshold of {threshold:.1f}%{action}."
    return _alert(metric, status, value, threshold, explanation)


def _activity_decline_pct(weekly_activity: Optional[pd.DataFrame]) -> Optional[float]:
    """Calculate the latest week-over-week activity decline, when available."""
    if weekly_activity is None or weekly_activity.empty:
        return None
    metric_column = next(
        (column for column in ["active_learners", "avg_active_minutes", "avg_session_duration", "total_duration_minutes"] if column in weekly_activity.columns),
        None,
    )
    if metric_column is None or len(weekly_activity) < 2:
        return None
    activity = weekly_activity.copy()
    week_column = next((column for column in ["activity_week", "week", "session_start"] if column in activity.columns), None)
    if week_column:
        activity[week_column] = pd.to_datetime(activity[week_column], errors="coerce")
        activity = activity.sort_values(week_column)
    values = pd.to_numeric(activity[metric_column], errors="coerce").dropna()
    if len(values) < 2 or values.iloc[-2] <= 0:
        return None
    return max(0.0, (values.iloc[-2] - values.iloc[-1]) / values.iloc[-2] * 100.0)


def evaluate_metric_alerts(
    kpis: Dict[str, Any],
    thresholds: AlertThresholds = AlertThresholds(),
    weekly_activity: Optional[pd.DataFrame] = None,
    learner_activity: Optional[pd.DataFrame] = None,
) -> List[MetricAlert]:
    """Evaluate all configured metrics using live KPI and analytical-view data."""
    decline_warning = thresholds.engagement_decline_warning_pct or thresholds.activity_decline_warning_pct
    decline_critical = thresholds.engagement_decline_critical_pct or thresholds.activity_decline_critical_pct
    total_learners = _number(kpis.get("total_students"))
    at_risk_count = _number(kpis.get("at_risk_learner_count"))
    at_risk_pct = (
        at_risk_count / total_learners * 100.0
        if total_learners and at_risk_count is not None and total_learners > 0
        else _number(kpis.get("at_risk_percentage_pct"))
    )
    engagement_rate = _number(kpis.get("engagement_rate_pct", kpis.get("avg_engagement_score")))
    if engagement_rate is None and learner_activity is not None and "engagement_score" in learner_activity:
        scores = pd.to_numeric(learner_activity["engagement_score"], errors="coerce").dropna()
        engagement_rate = float(scores.mean()) if not scores.empty else None

    weekly_active = None
    if weekly_activity is not None and not weekly_activity.empty and "active_learners" in weekly_activity:
        weekly = weekly_activity.copy()
        if "activity_week" in weekly.columns:
            weekly = weekly.sort_values("activity_week")
        weekly_active = _number(weekly.iloc[-1]["active_learners"])

    return [
        _percentage_alert("Dropout Rate", _number(kpis.get("dropout_rate_pct")), thresholds.dropout_warning_pct, thresholds.dropout_critical_pct, "Dropout rate", True),
        _percentage_alert("Completion Rate", _number(kpis.get("completion_rate_pct")), thresholds.completion_warning_pct, thresholds.completion_critical_pct, "Completion rate", False),
        _percentage_alert("At-Risk Student Percentage", at_risk_pct, thresholds.at_risk_warning_pct, thresholds.at_risk_critical_pct, "At-risk student percentage", True),
        _minimum_alert("Weekly Active Learners", weekly_active, thresholds.weekly_active_learners_warning, thresholds.weekly_active_learners_critical, "Weekly active learners"),
        _percentage_alert("Engagement Rate", engagement_rate, thresholds.engagement_rate_warning_pct, thresholds.engagement_rate_critical_pct, "Engagement rate", False),
        _percentage_alert("Significant Activity Decline", _activity_decline_pct(weekly_activity), decline_warning, decline_critical, "Activity decline", True),
    ]


def overall_alert_status(alerts: List[MetricAlert]) -> str:
    """Return the highest severity across the monitored metrics."""
    statuses = {alert.status for alert in alerts}
    if CRITICAL in statuses:
        return CRITICAL
    if WARNING in statuses:
        return WARNING
    return NORMAL
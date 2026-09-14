"""Configurable business-metric threshold monitoring for the dashboard."""

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
    engagement_decline_warning_pct: float = 10.0
    engagement_decline_critical_pct: float = 25.0


@dataclass(frozen=True)
class MetricAlert:
    """A business-readable result for one monitored metric."""

    metric: str
    status: str
    observed_value: float
    threshold: Optional[float]
    explanation: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "metric": self.metric,
            "status": self.status,
            "observed_value": self.observed_value,
            "threshold": self.threshold,
            "explanation": self.explanation,
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
) -> MetricAlert:
    return MetricAlert(metric, status, round(float(value), 2), threshold, explanation)


def _threshold_explanation(
    status: str,
    value: float,
    normal_text: str,
    action_text: str,
) -> str:
    if status == NORMAL:
        return normal_text
    return f"{value:.1f}% {action_text}"


def _engagement_decline_pct(weekly_activity: Optional[pd.DataFrame]) -> Optional[float]:
    """Calculate the latest week-over-week active-minute decline, when available."""
    if weekly_activity is None or weekly_activity.empty:
        return None
    metric_column = next(
        (column for column in ["avg_active_minutes", "avg_session_duration", "total_duration_minutes"] if column in weekly_activity.columns),
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
) -> List[MetricAlert]:
    """Evaluate configured thresholds and return one alert per monitored metric."""
    dropout_rate = float(kpis.get("dropout_rate_pct", 0.0) or 0.0)
    completion_rate = float(kpis.get("completion_rate_pct", 0.0) or 0.0)
    total_learners = int(kpis.get("total_students", 0) or 0)
    at_risk_count = int(kpis.get("at_risk_learner_count", 0) or 0)
    at_risk_pct = (at_risk_count / total_learners * 100.0) if total_learners else 0.0

    dropout_status = _higher_is_worse(dropout_rate, thresholds.dropout_warning_pct, thresholds.dropout_critical_pct)
    completion_status = _lower_is_worse(completion_rate, thresholds.completion_warning_pct, thresholds.completion_critical_pct)
    risk_status = _higher_is_worse(at_risk_pct, thresholds.at_risk_warning_pct, thresholds.at_risk_critical_pct)
    alerts = [
        _alert("Dropout rate", dropout_status, dropout_rate, thresholds.dropout_warning_pct, _threshold_explanation(
            dropout_status, dropout_rate, "Dropout rate is within the retention policy.", "of selected learners are dropped; retention intervention is needed."
        )),
        _alert("Completion rate", completion_status, completion_rate, thresholds.completion_warning_pct, _threshold_explanation(
            completion_status, completion_rate, "Completion rate is within the success policy.", "of selected learners are completing courses; review course friction and engagement."
        )),
        _alert("At-risk learner population", risk_status, at_risk_pct, thresholds.at_risk_warning_pct, _threshold_explanation(
            risk_status, at_risk_pct, "At-risk learner population is within the support policy.", "of selected learners are high or critical risk; prioritize targeted support."
        )),
    ]

    decline = _engagement_decline_pct(weekly_activity)
    if decline is not None:
        alerts.append(
            _alert(
                "Engagement decline",
                _higher_is_worse(
                    decline,
                    thresholds.engagement_decline_warning_pct,
                    thresholds.engagement_decline_critical_pct,
                ),
                decline,
                thresholds.engagement_decline_warning_pct,
                "Engagement is stable week over week."
                if _higher_is_worse(decline, thresholds.engagement_decline_warning_pct, thresholds.engagement_decline_critical_pct) == NORMAL
                else f"Average activity declined {decline:.1f}% week over week; investigate emerging disengagement.",
            )
        )
    else:
        alerts.append(
            _alert(
                "Engagement decline",
                NORMAL,
                0.0,
                thresholds.engagement_decline_warning_pct,
                "Not enough consecutive activity periods are available to detect a sudden engagement decline.",
            )
        )
    return alerts


def overall_alert_status(alerts: List[MetricAlert]) -> str:
    """Return the highest severity across the monitored metrics."""
    statuses = {alert.status for alert in alerts}
    if CRITICAL in statuses:
        return CRITICAL
    if WARNING in statuses:
        return WARNING
    return NORMAL
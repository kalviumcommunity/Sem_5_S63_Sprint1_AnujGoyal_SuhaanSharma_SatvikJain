"""Tests for configurable dashboard metric threshold monitoring."""

import pandas as pd

from dashboard.alerts import (
    CRITICAL,
    NORMAL,
    WARNING,
    AlertThresholds,
    evaluate_metric_alerts,
    overall_alert_status,
)


def kpis(completion=75.0, dropout=10.0, total=100, at_risk=10, engagement=75.0):
    return {
        "completion_rate_pct": completion,
        "dropout_rate_pct": dropout,
        "total_students": total,
        "at_risk_learner_count": at_risk,
        "engagement_rate_pct": engagement,
    }


def test_normal_metrics_produce_normal_alerts():
    alerts = evaluate_metric_alerts(
        kpis(),
        weekly_activity=pd.DataFrame({"active_learners": [120, 110], "avg_active_minutes": [30, 29]}),
    )

    assert overall_alert_status(alerts) == NORMAL
    assert all(alert.status == NORMAL for alert in alerts)


def test_warning_thresholds_are_configurable():
    thresholds = AlertThresholds(
        dropout_warning_pct=5.0,
        dropout_critical_pct=20.0,
        completion_warning_pct=80.0,
        completion_critical_pct=50.0,
        at_risk_warning_pct=15.0,
        at_risk_critical_pct=35.0,
        engagement_decline_warning_pct=5.0,
        engagement_decline_critical_pct=20.0,
    )
    alerts = evaluate_metric_alerts(
        kpis(completion=75, dropout=10, at_risk=20),
        thresholds,
        weekly_activity=pd.DataFrame({"active_learners": [120, 110]}),
    )

    assert overall_alert_status(alerts) == WARNING
    assert alerts[0].status == WARNING
    assert alerts[1].status == WARNING
    assert "retention intervention" in alerts[0].explanation


def test_critical_metrics_and_engagement_decline_are_reported():
    alerts = evaluate_metric_alerts(
        kpis(completion=35, dropout=40, at_risk=50, engagement=35),
        weekly_activity=pd.DataFrame({"active_learners": [100, 40]}),
    )

    assert overall_alert_status(alerts) == CRITICAL
    assert alerts[0].status == CRITICAL
    assert alerts[1].status == CRITICAL
    assert alerts[2].status == CRITICAL
    assert alerts[3].status == CRITICAL
    assert alerts[4].status == CRITICAL
    assert alerts[5].status == CRITICAL
    assert alerts[5].observed_value == 60.0


def test_missing_activity_history_is_explained_without_false_alert():
    alerts = evaluate_metric_alerts(kpis(), weekly_activity=pd.DataFrame())

    engagement_alert = alerts[-1]
    assert engagement_alert.status == NORMAL
    assert "Not enough" in engagement_alert.explanation
    assert engagement_alert.data_available is False


def test_all_required_metrics_are_returned_in_order():
    alerts = evaluate_metric_alerts(
        kpis(),
        weekly_activity=pd.DataFrame({"active_learners": [120, 110]}),
    )

    assert [alert.metric for alert in alerts] == [
        "Dropout Rate",
        "Completion Rate",
        "At-Risk Student Percentage",
        "Weekly Active Learners",
        "Engagement Rate",
        "Significant Activity Decline",
    ]


def test_missing_kpi_is_not_treated_as_zero():
    alerts = evaluate_metric_alerts(
        {"total_students": 100, "at_risk_learner_count": 10},
        weekly_activity=pd.DataFrame({"active_learners": [120]}),
    )

    dropout_alert = alerts[0]
    assert dropout_alert.status == NORMAL
    assert dropout_alert.data_available is False
    assert dropout_alert.observed_value == 0.0
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


def kpis(completion=75.0, dropout=10.0, total=100, at_risk=10):
    return {
        "completion_rate_pct": completion,
        "dropout_rate_pct": dropout,
        "total_students": total,
        "at_risk_learner_count": at_risk,
    }


def test_normal_metrics_produce_normal_alerts():
    alerts = evaluate_metric_alerts(kpis(), weekly_activity=pd.DataFrame({"avg_active_minutes": [30, 29]}))

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
    alerts = evaluate_metric_alerts(kpis(completion=75, dropout=10, at_risk=20), thresholds)

    assert overall_alert_status(alerts) == WARNING
    assert alerts[0].status == WARNING
    assert alerts[1].status == WARNING
    assert "retention intervention" in alerts[0].explanation


def test_critical_metrics_and_engagement_decline_are_reported():
    alerts = evaluate_metric_alerts(
        kpis(completion=35, dropout=40, at_risk=50),
        weekly_activity=pd.DataFrame({"avg_active_minutes": [100, 60]}),
    )

    assert overall_alert_status(alerts) == CRITICAL
    assert alerts[0].status == CRITICAL
    assert alerts[1].status == CRITICAL
    assert alerts[2].status == CRITICAL
    assert alerts[3].status == CRITICAL
    assert alerts[3].observed_value == 40.0


def test_missing_activity_history_is_explained_without_false_alert():
    alerts = evaluate_metric_alerts(kpis(), weekly_activity=pd.DataFrame())

    engagement_alert = alerts[-1]
    assert engagement_alert.status == NORMAL
    assert "Not enough" in engagement_alert.explanation
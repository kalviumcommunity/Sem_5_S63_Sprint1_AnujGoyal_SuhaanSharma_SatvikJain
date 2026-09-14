"""Tests for periodic insight summaries and optional email delivery."""

import pandas as pd

from dashboard.alerts import WARNING, MetricAlert
from dashboard.sharing import (
    DeliveryResult,
    PeriodicSummary,
    SmtpEmailSender,
    build_periodic_summary,
)


def test_periodic_summary_contains_kpis_trends_alerts_and_insights():
    alerts = [MetricAlert("Dropout rate", WARNING, 24.0, 20.0, "Retention intervention is needed.")]
    views = {
        "course_performance_view": pd.DataFrame({
            "course_title": ["Python", "SQL"],
            "completion_rate_pct": [82.0, 55.0],
        })
    }

    summary = build_periodic_summary(
        {
            "completion_rate_pct": 72.0,
            "dropout_rate_pct": 24.0,
            "active_learner_count": 100,
            "at_risk_learner_count": 30,
            "avg_quiz_score_pct": 79.0,
            "avg_session_duration_minutes": 42.0,
        },
        views,
        alerts,
    )

    assert isinstance(summary, PeriodicSummary)
    assert "Completion rate: 72.0%" in summary.plain_text
    assert "Strongest course completion: Python" in summary.markdown
    assert "WARNING: Dropout rate" in summary.markdown
    assert "Important Insights" in summary.markdown


def test_email_sender_is_safe_when_environment_is_not_configured():
    sender = SmtpEmailSender(environ={})
    result = sender.send("stakeholder@example.com", PeriodicSummary("Subject", "# Report", "Report"))

    assert isinstance(result, DeliveryResult)
    assert result.status == "NOT_CONFIGURED"
    assert "SMTP environment variables" in result.message


def test_email_sender_rejects_empty_recipient_before_delivery():
    sender = SmtpEmailSender(environ={
        "LEARNING_ANALYTICS_SMTP_HOST": "smtp.example.com",
        "LEARNING_ANALYTICS_SMTP_USERNAME": "user",
        "LEARNING_ANALYTICS_SMTP_PASSWORD": "secret",
        "LEARNING_ANALYTICS_REPORT_FROM": "reports@example.com",
    })

    result = sender.send("", PeriodicSummary("Subject", "# Report", "Report"))

    assert result.status == "INVALID_RECIPIENT"
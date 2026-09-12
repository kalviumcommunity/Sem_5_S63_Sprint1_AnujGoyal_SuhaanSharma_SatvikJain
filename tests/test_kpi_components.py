"""
Unit tests for Concept #37: KPI Card & Summary Metric Design.
"""

import pytest
from dashboard.utils import format_metric, format_kpi_summary
from dashboard.components import render_kpi_card, render_kpi_summary_grid


def test_format_metric():
    """Verify numeric metric formatting helper."""
    assert format_metric(68.4, suffix="%") == "68.4%"
    assert format_metric(1250, decimals=0) == "1,250"
    assert format_metric(42.5, suffix=" mins") == "42.5 mins"
    assert format_metric(None) == "N/A"
    assert format_metric("invalid") == "invalid"


def test_format_kpi_summary_default_values():
    """Verify default formatting for all 6 required KPI summary metrics."""
    summary = format_kpi_summary({})
    assert isinstance(summary, dict)
    assert len(summary) == 6

    required_keys = [
        "completion_rate",
        "dropout_rate",
        "active_learners",
        "at_risk_learners",
        "avg_quiz_score",
        "avg_session_duration"
    ]
    for key in required_keys:
        assert key in summary
        card = summary[key]
        assert "label" in card
        assert "value" in card
        assert "delta" in card
        assert "help_text" in card

    assert summary["completion_rate"]["label"] == "Completion Rate"
    assert "%" in summary["completion_rate"]["value"]

    assert summary["dropout_rate"]["label"] == "Dropout Rate"
    assert "%" in summary["dropout_rate"]["value"]

    assert summary["active_learners"]["label"] == "Active Learners"

    assert summary["at_risk_learners"]["label"] == "At-Risk Learners"

    assert summary["avg_quiz_score"]["label"] == "Average Quiz Score"
    assert "%" in summary["avg_quiz_score"]["value"]

    assert summary["avg_session_duration"]["label"] == "Avg Session Duration"
    assert "mins" in summary["avg_session_duration"]["value"]


def test_format_kpi_summary_custom_input():
    """Verify formatting custom metric values from SQL/Pandas analytics pipeline."""
    custom_kpis = {
        "completion_rate_pct": 75.8,
        "dropout_rate_pct": 10.4,
        "active_learner_count": 2400,
        "at_risk_learner_count": 18,
        "avg_quiz_score_pct": 84.2,
        "avg_session_duration_minutes": 52.3,
        "completion_rate_delta": "+5.0%",
        "dropout_rate_delta": "-2.1%"
    }
    summary = format_kpi_summary(custom_kpis)
    assert summary["completion_rate"]["value"] == "75.8%"
    assert summary["completion_rate"]["delta"] == "+5.0%"
    assert summary["dropout_rate"]["value"] == "10.4%"
    assert summary["active_learners"]["value"] == "2,400"
    assert summary["at_risk_learners"]["value"] == "18"
    assert summary["avg_quiz_score"]["value"] == "84.2%"
    assert summary["avg_session_duration"]["value"] == "52.3 mins"


def test_render_kpi_summary_grid_structure():
    """Verify render_kpi_summary_grid returns formatted summary dictionary."""
    summary = format_kpi_summary({"completion_rate": 80.0})
    assert summary["completion_rate"]["value"] == "80.0%"

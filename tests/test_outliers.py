"""
Unit tests for Concept #13: Outlier Detection with Statistical Methods.
Tests IQR, Z-Score, domain anomaly checks, non-destructive tagging, and audit scorecard generation.
"""

import pytest
import pandas as pd
import numpy as np

from src.outliers import (
    calculate_iqr_bounds,
    calculate_zscore,
    detect_column_outliers,
    tag_dataset_outliers,
    generate_outlier_scorecard,
    OutlierReport,
    ColumnOutlierSummary
)


@pytest.fixture
def sample_session_durations():
    """Provides a sample dataset of session durations with mild, extreme, and anomalous values."""
    # Typical values around 20-60 mins, plus some extreme values (300 mins) and an anomaly (-5 mins, 999 mins)
    return pd.Series([
        20.0, 25.0, 28.0, 30.0, 32.0, 35.0, 40.0, 42.0, 45.0, 50.0,
        55.0, 60.0, 65.0, 300.0, -5.0, 999.0
    ])


@pytest.fixture
def sample_quiz_scores():
    """Provides quiz scores with normal distribution plus impossible scores (150%, -10%)."""
    return pd.Series([
        65.0, 70.0, 72.0, 75.0, 78.0, 80.0, 82.0, 85.0, 88.0, 90.0,
        92.0, 95.0, 150.0, -10.0
    ])


def test_calculate_iqr_bounds():
    """Test IQR statistical boundary calculations."""
    data = pd.Series([10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
    q1, q3, iqr, lower, upper = calculate_iqr_bounds(data, multiplier=1.5)

    assert q1 < q3
    assert iqr == (q3 - q1)
    assert lower == (q1 - 1.5 * iqr)
    assert upper == (q3 + 1.5 * iqr)


def test_calculate_zscore():
    """Test standard Z-score calculation."""
    data = pd.Series([10.0, 10.0, 10.0, 10.0, 100.0])
    z_scores, mean, std = calculate_zscore(data)

    assert mean > 10.0
    assert std > 0.0
    assert z_scores.iloc[4] > 1.5  # 100 has large positive z-score


def test_detect_column_outliers_iqr(sample_session_durations):
    """Test IQR outlier detection and anomaly classification on session durations."""
    class_series, summary = detect_column_outliers(
        sample_session_durations,
        column_name="duration_minutes",
        method="iqr"
    )

    assert isinstance(summary, ColumnOutlierSummary)
    assert summary.outlier_count > 0
    assert summary.domain_anomalies_count >= 2  # -5.0 and 999.0 violate domain limits (0.1 - 720.0)
    assert "Domain Anomaly" in class_series.values
    assert "Extreme Outlier" in class_series.values or "Mild Outlier" in class_series.values
    assert "Normal" in class_series.values


def test_detect_column_outliers_zscore(sample_quiz_scores):
    """Test Z-score outlier detection and domain checks on quiz scores."""
    class_series, summary = detect_column_outliers(
        sample_quiz_scores,
        column_name="score_percentage",
        method="zscore"
    )

    assert summary.domain_anomalies_count == 2  # 150.0 and -10.0 exceed 0-100%
    assert summary.outlier_count >= 2


def test_tag_dataset_outliers_non_destructive():
    """Test that tag_dataset_outliers preserves all rows and adds diagnostic columns."""
    df = pd.DataFrame({
        "session_id": ["S1", "S2", "S3", "S4"],
        "duration_minutes": [30.0, 45.0, 500.0, -10.0],
        "active_minutes": [25.0, 40.0, 480.0, 0.0]
    })
    initial_len = len(df)
    enriched_df, report = tag_dataset_outliers(df, entity_name="sessions", method="iqr")

    # Critical: Non-destructive verification
    assert len(enriched_df) == initial_len
    assert "duration_minutes_is_outlier" in enriched_df.columns
    assert "duration_minutes_outlier_class" in enriched_df.columns
    assert isinstance(report, OutlierReport)
    assert report.total_records == 4
    assert report.records_with_outliers > 0


def test_generate_outlier_scorecard(sample_session_durations):
    """Test multi-dataset comparative outlier scorecard generation."""
    df = pd.DataFrame({"duration_minutes": sample_session_durations})
    _, report = tag_dataset_outliers(df, entity_name="sessions")
    scorecard = generate_outlier_scorecard({"sessions": report})

    assert isinstance(scorecard, pd.DataFrame)
    assert len(scorecard) > 0
    assert "Dataset" in scorecard.columns
    assert "Variable" in scorecard.columns
    assert "Outliers Count" in scorecard.columns
    assert "Domain Anomalies" in scorecard.columns

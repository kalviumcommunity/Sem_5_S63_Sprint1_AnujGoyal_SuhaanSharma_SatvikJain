"""
Unit tests for Concept #35: Business Visualization Principles.
"""

import pytest
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from src.visualization import (
    PRIMARY_BLUE,
    SUCCESS_GREEN,
    DANGER_RED,
    RISK_COLOR_MAP,
    COLOR_PALETTES,
    apply_business_theme,
    create_category_bar_chart,
    create_trend_line_chart,
    create_correlation_scatter_chart,
    create_distribution_histogram,
    create_cohort_heatmap,
    validate_visualization_config,
)


@pytest.fixture
def sample_course_performance_df():
    """Fixture providing sample course performance DataFrame for testing visualization generators."""
    return pd.DataFrame({
        "course_title": ["Python Fundamentals", "SQL Database Analytics", "Machine Learning Basics", "Data Viz with Plotly"],
        "completion_rate_pct": [78.4, 62.1, 45.0, 81.2],
        "category": ["Programming", "Database", "Data Science", "Visualization"],
        "learner_count": [450, 320, 210, 270]
    })


@pytest.fixture
def sample_trend_df():
    """Fixture providing sample weekly trend DataFrame."""
    return pd.DataFrame({
        "week": [f"Week {i}" for i in range(1, 6)],
        "active_study_hours": [3.2, 4.1, 4.8, 4.5, 5.2],
        "cohort": ["Cohort A"] * 5
    })


@pytest.fixture
def sample_correlation_df():
    """Fixture providing sample correlation DataFrame."""
    return pd.DataFrame({
        "quiz_avg_score": [85.0, 92.0, 65.0, 40.0, 78.0],
        "completion_rate_pct": [80.0, 95.0, 50.0, 10.0, 70.0],
        "dropout_risk_level": ["Low", "Low", "Moderate", "Critical", "Low"],
        "session_count": [12, 18, 8, 3, 10]
    })


def test_color_palettes_and_constants():
    """Verify color constants and semantic risk color map definitions."""
    assert PRIMARY_BLUE == "#1E88E5"
    assert RISK_COLOR_MAP["Completed"] == SUCCESS_GREEN
    assert RISK_COLOR_MAP["Dropped"] == DANGER_RED
    assert "categorical" in COLOR_PALETTES
    assert len(COLOR_PALETTES["categorical"]) >= 4


def test_apply_business_theme():
    """Verify applying executive theme to Plotly figure."""
    fig = go.Figure()
    fig = apply_business_theme(
        fig,
        title="Python Course Completion Achieves 78.4% Benchmark",
        x_title="Course Category",
        y_title="Completion Rate",
        unit="%"
    )
    layout = fig.layout
    assert "Python Course Completion" in layout.title.text
    assert layout.xaxis.title.text == "Course Category"
    assert layout.yaxis.title.text == "Completion Rate (%)"
    assert layout.paper_bgcolor == "white"


def test_create_category_bar_chart(sample_course_performance_df):
    """Verify bar chart creation, zero-baseline enforcement, and sorting."""
    fig = create_category_bar_chart(
        df=sample_course_performance_df,
        x_col="course_title",
        y_col="completion_rate_pct",
        title="Course Completion Rates Across Categories (%)",
        x_title="Course",
        y_title="Completion Rate",
        unit="%",
        sort_descending=True,
        risk_threshold=50.0
    )
    assert isinstance(fig, go.Figure)

    # Verify zero baseline rule on Y-axis
    y_range = fig.layout.yaxis.range
    assert y_range is not None
    assert y_range[0] == 0  # Enforces 0 baseline

    # Verify actionable title
    assert "Course Completion Rates Across Categories" in fig.layout.title.text


def test_create_trend_line_chart(sample_trend_df):
    """Verify time-series line chart builder."""
    fig = create_trend_line_chart(
        df=sample_trend_df,
        x_col="week",
        y_col="active_study_hours",
        title="Weekly Active Study Duration Increases 62.5% Over 5 Weeks",
        x_title="Week",
        y_title="Active Study Duration",
        unit="hrs"
    )
    assert isinstance(fig, go.Figure)
    assert fig.layout.yaxis.title.text == "Active Study Duration (hrs)"


def test_create_correlation_scatter_chart(sample_correlation_df):
    """Verify correlation scatter chart builder."""
    fig = create_correlation_scatter_chart(
        df=sample_correlation_df,
        x_col="quiz_avg_score",
        y_col="completion_rate_pct",
        color_col="dropout_risk_level",
        size_col="session_count",
        title="High Quiz Scores Strongly Correlate with Course Completion",
        x_title="Average Quiz Score",
        y_title="Completion Rate",
        unit="%"
    )
    assert isinstance(fig, go.Figure)
    assert len(fig.data) >= 1


def test_create_distribution_histogram(sample_correlation_df):
    """Verify distribution histogram builder."""
    fig = create_distribution_histogram(
        df=sample_correlation_df,
        col="quiz_avg_score",
        title="Distribution of Student Quiz Average Scores",
        x_title="Quiz Score",
        y_title="Student Count",
        unit="%",
        nbins=10
    )
    assert isinstance(fig, go.Figure)
    assert fig.layout.yaxis.range[0] == 0


def test_create_cohort_heatmap():
    """Verify 2D matrix cohort heatmap builder."""
    df = pd.DataFrame({
        "day_of_week": ["Mon", "Mon", "Tue", "Tue"],
        "hour_bucket": ["Morning", "Evening", "Morning", "Evening"],
        "activity_score": [85.0, 42.0, 90.0, 60.0]
    })
    fig = create_cohort_heatmap(
        df=df,
        x_col="hour_bucket",
        y_col="day_of_week",
        z_col="activity_score",
        title="Learner Activity Peak Heatmap",
        x_title="Time Bucket",
        y_title="Day of Week",
        unit="pts"
    )
    assert isinstance(fig, go.Figure)


def test_validate_visualization_config_valid():
    """Verify validation helper with a compliant configuration."""
    valid_config = {
        "chart_type": "bar",
        "title": "Course Completion Rate Breakdown by Category (%)",
        "x_title": "Category",
        "y_title": "Completion Rate",
        "unit": "%",
        "zero_baseline": True
    }
    report = validate_visualization_config(valid_config)
    assert report["is_valid"] is True
    assert len(report["violations"]) == 0


def test_validate_visualization_config_invalid():
    """Verify validation helper catches rule violations."""
    invalid_config = {
        "chart_type": "3d_bar",  # Unsupported
        "title": "Short",        # Not actionable (< 3 words)
        "x_title": "",           # Missing X title
        "y_title": "",           # Missing Y title
        "unit": None,            # Unit missing
        "zero_baseline": False   # Bar chart zero baseline violation
    }
    report = validate_visualization_config(invalid_config)
    assert report["is_valid"] is False
    assert len(report["violations"]) >= 4


def test_empty_dataframe_handling():
    """Verify chart generators handle empty DataFrames gracefully without crashing."""
    empty_df = pd.DataFrame()
    fig1 = create_category_bar_chart(empty_df, "x", "y", "Empty Bar Chart Title")
    fig2 = create_trend_line_chart(empty_df, "x", "y", "Empty Line Chart Title")
    fig3 = create_correlation_scatter_chart(empty_df, "x", "y", "Empty Scatter Chart Title")
    fig4 = create_distribution_histogram(empty_df, "x", "Empty Histogram Title")
    fig5 = create_cohort_heatmap(empty_df, "x", "y", "z", "Empty Heatmap Title")

    for fig in [fig1, fig2, fig3, fig4, fig5]:
        assert isinstance(fig, go.Figure)

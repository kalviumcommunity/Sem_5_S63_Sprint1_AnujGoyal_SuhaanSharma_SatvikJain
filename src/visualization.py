"""
Business Visualization Principles & Standardized Chart Configurator.

Provides unified styling, color palettes, executive layout configurations,
and analytical chart builders compliant with project visualization rules.
"""

from typing import Dict, Any, Optional, Union, List
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from src.utils import setup_logger

logger = setup_logger(__name__)

# Executive Color Palette Constants
PRIMARY_BLUE = "#1E88E5"
SECONDARY_TEAL = "#00ACC1"
ACCENT_PURPLE = "#8E24AA"
SUCCESS_GREEN = "#43A047"
WARNING_AMBER = "#FB8C00"
DANGER_RED = "#E53935"
NEUTRAL_GRAY = "#78909C"
BACKGROUND_LIGHT = "#F8F9FA"
TEXT_DARK = "#263238"

# Semantic Color Maps
RISK_COLOR_MAP = {
    "Low": SUCCESS_GREEN,
    "Moderate": WARNING_AMBER,
    "High": DANGER_RED,
    "Critical": "#B71C1C",
    "Completed": SUCCESS_GREEN,
    "In Progress": PRIMARY_BLUE,
    "Dropped": DANGER_RED
}

COLOR_PALETTES = {
    "sequential": [PRIMARY_BLUE, SECONDARY_TEAL, "#00838F", "#006064"],
    "categorical": [PRIMARY_BLUE, SECONDARY_TEAL, ACCENT_PURPLE, WARNING_AMBER, SUCCESS_GREEN],
    "risk": [SUCCESS_GREEN, WARNING_AMBER, DANGER_RED, "#B71C1C"]
}


def apply_business_theme(
    fig: go.Figure,
    title: str,
    x_title: Optional[str] = None,
    y_title: Optional[str] = None,
    unit: str = "",
    height: int = 450,
    width: Optional[int] = None,
    hovermode: str = "closest"
) -> go.Figure:
    """
    Applies standard executive formatting, high contrast, clean gridlines,
    and responsive layout rules to a Plotly figure.

    Args:
        fig: Plotly Figure instance
        title: Actionable chart title
        x_title: X-axis title
        y_title: Y-axis title
        unit: Metric unit indicator
        height: Chart height in pixels
        width: Optional fixed width
        hovermode: Hover interaction mode

    Returns:
        Formatted Plotly Figure
    """
    formatted_y_title = f"{y_title} ({unit})" if y_title and unit and f"({unit})" not in y_title else (y_title or "")

    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>",
            font=dict(size=16, color=TEXT_DARK, family="Arial, sans-serif"),
            x=0.0,
            xanchor="left"
        ),
        xaxis=dict(
            title=dict(text=x_title or "", font=dict(size=12, color=TEXT_DARK)),
            showgrid=False,
            showline=True,
            linecolor="#CFD8DC",
            ticks="outside"
        ),
        yaxis=dict(
            title=dict(text=formatted_y_title, font=dict(size=12, color=TEXT_DARK)),
            showgrid=True,
            gridcolor="#ECEFF1",
            showline=True,
            linecolor="#CFD8DC",
            zeroline=True,
            zerolinecolor="#B0BEC5"
        ),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Arial, sans-serif", size=12, color=TEXT_DARK),
        margin=dict(l=50, r=40, t=60, b=50),
        height=height,
        width=width,
        hovermode=hovermode
    )
    return fig


def create_category_bar_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    x_title: Optional[str] = None,
    y_title: Optional[str] = None,
    unit: str = "%",
    sort_descending: bool = True,
    risk_threshold: Optional[float] = None,
    orientation: str = "v",
    color_col: Optional[str] = None
) -> go.Figure:
    """
    Creates a standardized categorical bar chart compliant with visualization principles:
    - Enforces zero baseline on quantitative axis
    - Sorts categories by value
    - Applies actionable title and clear units
    """
    if df.empty:
        fig = go.Figure()
        return apply_business_theme(fig, title=title, x_title=x_title, y_title=y_title, unit=unit)

    chart_df = df.copy()

    # Sort categories
    if sort_descending:
        chart_df = chart_df.sort_values(by=y_col, ascending=(orientation == "h"))

    if orientation == "v":
        fig = px.bar(
            chart_df,
            x=x_col,
            y=y_col,
            color=color_col or x_col if color_col in chart_df.columns else None,
            text_auto=".1f" if unit == "%" else True,
            color_discrete_map=RISK_COLOR_MAP if color_col in RISK_COLOR_MAP else None,
            color_discrete_sequence=COLOR_PALETTES["categorical"]
        )
        # Enforce zero baseline on Y axis
        max_val = float(chart_df[y_col].max()) if not chart_df[y_col].empty else 100.0
        y_max = max(max_val * 1.15, 1.0)
        fig.update_yaxes(range=[0, y_max])
    else:
        fig = px.bar(
            chart_df,
            x=y_col,
            y=x_col,
            orientation="h",
            color=color_col or x_col if color_col in chart_df.columns else None,
            text_auto=".1f" if unit == "%" else True,
            color_discrete_sequence=COLOR_PALETTES["categorical"]
        )
        max_val = float(chart_df[y_col].max()) if not chart_df[y_col].empty else 100.0
        fig.update_xaxes(range=[0, max_val * 1.15])

    # Optional threshold benchmark line
    if risk_threshold is not None:
        if orientation == "v":
            fig.add_hline(
                y=risk_threshold,
                line_dash="dash",
                line_color=DANGER_RED,
                annotation_text=f"Threshold ({risk_threshold}{unit})",
                annotation_position="top right"
            )
        else:
            fig.add_vline(
                x=risk_threshold,
                line_dash="dash",
                line_color=DANGER_RED,
                annotation_text=f"Threshold ({risk_threshold}{unit})",
                annotation_position="top right"
            )

    fig = apply_business_theme(
        fig,
        title=title,
        x_title=x_title or x_col.replace("_", " ").title(),
        y_title=y_title or y_col.replace("_", " ").title(),
        unit=unit
    )
    return fig


def create_trend_line_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    x_title: Optional[str] = None,
    y_title: Optional[str] = None,
    unit: str = "",
    group_col: Optional[str] = None
) -> go.Figure:
    """
    Creates a standardized time-series or trend line chart:
    - Chronologically ordered X-axis
    - High-contrast lines and markers
    - Actionable title and unit format
    """
    if df.empty:
        fig = go.Figure()
        return apply_business_theme(fig, title=title, x_title=x_title, y_title=y_title, unit=unit)

    chart_df = df.copy()
    if pd.api.types.is_datetime64_any_dtype(chart_df[x_col]) or "date" in x_col.lower() or "week" in x_col.lower():
        chart_df = chart_df.sort_values(by=x_col, ascending=True)

    fig = px.line(
        chart_df,
        x=x_col,
        y=y_col,
        color=group_col,
        markers=True,
        color_discrete_sequence=COLOR_PALETTES["categorical"]
    )
    fig.update_traces(line=dict(width=3), marker=dict(size=7))

    fig = apply_business_theme(
        fig,
        title=title,
        x_title=x_title or x_col.replace("_", " ").title(),
        y_title=y_title or y_col.replace("_", " ").title(),
        unit=unit
    )
    return fig


def create_correlation_scatter_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    x_title: Optional[str] = None,
    y_title: Optional[str] = None,
    color_col: Optional[str] = None,
    size_col: Optional[str] = None,
    unit: str = ""
) -> go.Figure:
    """
    Creates a scatter or bubble chart to reveal analytical correlations:
    - Clear dimensional encoding
    - Zero/natural bounds
    - Non-decorative, insight-driven point layout
    """
    if df.empty:
        fig = go.Figure()
        return apply_business_theme(fig, title=title, x_title=x_title, y_title=y_title, unit=unit)

    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        color=color_col,
        size=size_col,
        color_discrete_sequence=COLOR_PALETTES["categorical"],
        color_discrete_map=RISK_COLOR_MAP if color_col in RISK_COLOR_MAP else None,
        hover_data=[col for col in [x_col, y_col, color_col, size_col] if col and col in df.columns]
    )
    fig.update_traces(marker=dict(opacity=0.85, line=dict(width=1, color="white")))

    fig = apply_business_theme(
        fig,
        title=title,
        x_title=x_title or x_col.replace("_", " ").title(),
        y_title=y_title or y_col.replace("_", " ").title(),
        unit=unit
    )
    return fig


def create_distribution_histogram(
    df: pd.DataFrame,
    col: str,
    title: str,
    x_title: Optional[str] = None,
    y_title: str = "Learner Count",
    unit: str = "",
    nbins: int = 20
) -> go.Figure:
    """
    Creates a binned distribution histogram with zero baseline.
    """
    if df.empty or col not in df.columns:
        fig = go.Figure()
        return apply_business_theme(fig, title=title, x_title=x_title, y_title=y_title, unit=unit)

    fig = px.histogram(
        df,
        x=col,
        nbins=nbins,
        color_discrete_sequence=[PRIMARY_BLUE]
    )
    fig.update_traces(marker=dict(line=dict(width=1, color="white")))
    fig.update_yaxes(range=[0, None])

    fig = apply_business_theme(
        fig,
        title=title,
        x_title=x_title or col.replace("_", " ").title(),
        y_title=y_title,
        unit=unit
    )
    return fig


def create_cohort_heatmap(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    z_col: str,
    title: str,
    x_title: Optional[str] = None,
    y_title: Optional[str] = None,
    unit: str = "%"
) -> go.Figure:
    """
    Creates a cohort density or interaction heatmap.
    """
    if df.empty:
        fig = go.Figure()
        return apply_business_theme(fig, title=title, x_title=x_title, y_title=y_title, unit=unit)

    pivot_df = df.pivot(index=y_col, columns=x_col, values=z_col).fillna(0)

    fig = px.imshow(
        pivot_df,
        labels=dict(x=x_title or x_col, y=y_title or y_col, color=f"{z_col} ({unit})"),
        color_continuous_scale="Blues",
        text_auto=".1f" if unit == "%" else True
    )

    fig = apply_business_theme(
        fig,
        title=title,
        x_title=x_title or x_col.replace("_", " ").title(),
        y_title=y_title or y_col.replace("_", " ").title(),
        unit=unit
    )
    return fig


def validate_visualization_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates a chart configuration dictionary against business visualization rules.

    Checks enforced:
    1. Chart type is supported ('bar', 'line', 'scatter', 'histogram', 'heatmap').
    2. Title is non-empty and actionable (contains at least 3 words).
    3. Axis labels are non-empty and present.
    4. Measurement unit is explicitly defined.
    5. Zero baseline rule is set to True for bar/histogram charts.

    Returns:
        Validation result dictionary with 'is_valid' boolean and list of 'violations'.
    """
    violations = []
    chart_type = config.get("chart_type", "").lower()
    title = config.get("title", "")
    x_title = config.get("x_title", "")
    y_title = config.get("y_title", "")
    unit = config.get("unit", None)
    zero_baseline = config.get("zero_baseline", True)

    supported_types = ["bar", "line", "scatter", "histogram", "heatmap"]
    if chart_type not in supported_types:
        violations.append(f"Unsupported chart_type '{chart_type}'. Must be one of {supported_types}.")

    if not title or len(title.split()) < 3:
        violations.append("Title must be non-empty and executive actionable (at least 3 words).")

    if not x_title:
        violations.append("X-axis title must be explicitly defined.")

    if not y_title:
        violations.append("Y-axis title must be explicitly defined.")

    if unit is None:
        violations.append("Measurement unit must be explicitly specified (use empty string '' if unitless).")

    if chart_type in ["bar", "histogram"] and not zero_baseline:
        violations.append("Bar and histogram charts MUST enforce a zero baseline (zero_baseline=True).")

    is_valid = len(violations) == 0
    logger.info(f"Visualization configuration validation complete. Valid: {is_valid}")
    return {
        "is_valid": is_valid,
        "violations": violations,
        "config_checked": config
    }


# -----------------------------------------------------------------------------
# Domain-Specific Interactive Analytical Visualization Builders
# -----------------------------------------------------------------------------

def plot_completion_vs_dropout(df: pd.DataFrame) -> go.Figure:
    """
    Creates an interactive Plotly bar chart comparing completion vs dropout counts/percentages.
    """
    title = "Course Completion vs Dropout Status Breakdown"
    if df.empty:
        fig = go.Figure()
        return apply_business_theme(fig, title=title, x_title="Status", y_title="Learner Count", unit="")

    chart_df = df.copy()
    if "completion_status" in chart_df.columns:
        status_counts = chart_df["completion_status"].value_counts().reset_index()
        status_counts.columns = ["completion_status", "count"]
    elif "status" in chart_df.columns:
        status_counts = chart_df["status"].value_counts().reset_index()
        status_counts.columns = ["completion_status", "count"]
    else:
        status_counts = pd.DataFrame({
            "completion_status": ["Completed", "In Progress", "Dropped"],
            "count": [0, 0, 0]
        })

    total = status_counts["count"].sum()
    status_counts["percentage"] = (status_counts["count"] / max(total, 1) * 100).round(1)

    fig = px.bar(
        status_counts,
        x="completion_status",
        y="count",
        color="completion_status",
        text=status_counts["percentage"].apply(lambda v: f"{v:.1f}%"),
        color_discrete_map=RISK_COLOR_MAP,
        custom_data=["percentage"]
    )

    fig.update_traces(
        hovertemplate="<b>Status:</b> %{x}<br>" +
                      "<b>Learner Count:</b> %{y:,.0f}<br>" +
                      "<b>Percentage:</b> %{customdata[0]:.1f}%<extra></extra>"
    )
    max_val = float(status_counts["count"].max()) if not status_counts["count"].empty else 10.0
    fig.update_yaxes(range=[0, max(max_val * 1.15, 1.0)])

    return apply_business_theme(
        fig,
        title=title,
        x_title="Completion Status",
        y_title="Learner Count",
        unit=""
    )


def plot_session_trends(df: pd.DataFrame) -> go.Figure:
    """
    Creates an interactive line chart displaying session activity duration and frequency over time.
    """
    title = "Weekly Active Study Duration & Session Frequency Trends"
    if df.empty:
        fig = go.Figure()
        return apply_business_theme(fig, title=title, x_title="Timeline", y_title="Duration", unit="mins")

    chart_df = df.copy()
    date_col = next((c for c in ["week", "session_start", "date", "week_start"] if c in chart_df.columns), None)
    duration_col = next((c for c in ["duration_minutes", "active_minutes", "average_session_duration", "avg_duration_minutes"] if c in chart_df.columns), None)

    if not date_col or not duration_col:
        fig = go.Figure()
        return apply_business_theme(fig, title=title, x_title="Timeline", y_title="Duration", unit="mins")

    chart_df = chart_df.sort_values(by=date_col)

    fig = px.line(
        chart_df,
        x=date_col,
        y=duration_col,
        markers=True,
        color_discrete_sequence=[PRIMARY_BLUE]
    )

    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=8, color=SECONDARY_TEAL),
        hovertemplate="<b>Period:</b> %{x}<br>" +
                      f"<b>{duration_col.replace('_', ' ').title()}:</b> %{{y:.1f}} mins<extra></extra>"
    )

    return apply_business_theme(
        fig,
        title=title,
        x_title=date_col.replace("_", " ").title(),
        y_title=duration_col.replace("_", " ").title(),
        unit="mins"
    )


def plot_quiz_performance(df: pd.DataFrame) -> go.Figure:
    """
    Creates an interactive box/histogram of quiz scores across courses or attempts with pass threshold.
    """
    title = "Quiz Score Distribution & Target Mastery Benchmark (70%)"
    if df.empty:
        fig = go.Figure()
        return apply_business_theme(fig, title=title, x_title="Quiz / Course", y_title="Score", unit="%")

    chart_df = df.copy()
    score_col = next((c for c in ["score_percentage", "quiz_average", "score", "avg_quiz_score"] if c in chart_df.columns), None)
    group_col = next((c for c in ["course_title", "course_id", "quiz_id", "attempt_number", "category"] if c in chart_df.columns), None)

    if not score_col:
        fig = go.Figure()
        return apply_business_theme(fig, title=title, x_title="Course / Attempt", y_title="Score", unit="%")

    if group_col:
        fig = px.box(
            chart_df,
            x=group_col,
            y=score_col,
            color=group_col,
            points="outliers",
            color_discrete_sequence=COLOR_PALETTES["categorical"]
        )
        fig.update_traces(
            hovertemplate="<b>Group:</b> %{x}<br>" +
                          "<b>Score:</b> %{y:.1f}%<extra></extra>"
        )
    else:
        fig = px.histogram(
            chart_df,
            x=score_col,
            nbins=15,
            color_discrete_sequence=[PRIMARY_BLUE]
        )
        fig.update_traces(
            hovertemplate="<b>Score Range:</b> %{x}%<br>" +
                          "<b>Count:</b> %{y}<extra></extra>"
        )

    # Benchmark threshold line
    fig.add_hline(
        y=70.0,
        line_dash="dash",
        line_color=WARNING_AMBER,
        annotation_text="Pass Benchmark (70%)",
        annotation_position="top right"
    )

    fig.update_yaxes(range=[0, 105])

    return apply_business_theme(
        fig,
        title=title,
        x_title=(group_col or score_col).replace("_", " ").title(),
        y_title="Score Percentage",
        unit="%"
    )


def plot_engagement(df: pd.DataFrame) -> go.Figure:
    """
    Creates an interactive scatter/distribution chart of student engagement scores vs course progress.
    """
    title = "Learner Engagement Score vs Course Progress Velocity"
    if df.empty:
        fig = go.Figure()
        return apply_business_theme(fig, title=title, x_title="Engagement Score", y_title="Progress", unit="%")

    chart_df = df.copy()
    eng_col = next((c for c in ["engagement_score", "learning_consistency"] if c in chart_df.columns), None)
    prog_col = next((c for c in ["course_progress", "completion_rate", "progress_velocity"] if c in chart_df.columns), None)
    risk_col = next((c for c in ["dropout_risk_level", "risk_level", "completion_status"] if c in chart_df.columns), None)

    if not eng_col or not prog_col:
        fig = go.Figure()
        return apply_business_theme(fig, title=title, x_title="Engagement Score", y_title="Progress", unit="%")

    fig = px.scatter(
        chart_df,
        x=eng_col,
        y=prog_col,
        color=risk_col,
        color_discrete_map=RISK_COLOR_MAP if risk_col in RISK_COLOR_MAP else None,
        color_discrete_sequence=COLOR_PALETTES["categorical"],
        hover_data=[c for c in ["student_id", "sessions_per_week", "days_since_last_activity"] if c in chart_df.columns]
    )

    fig.update_traces(
        marker=dict(size=10, opacity=0.8, line=dict(width=1, color="white")),
        hovertemplate="<b>Engagement Score:</b> %{x:.1f}<br>" +
                      "<b>Progress:</b> %{y:.1f}%<extra></extra>"
    )

    return apply_business_theme(
        fig,
        title=title,
        x_title=eng_col.replace("_", " ").title(),
        y_title=prog_col.replace("_", " ").title(),
        unit="%"
    )


def plot_behavioural_segments(df: pd.DataFrame) -> go.Figure:
    """
    Creates an interactive scatter/bubble chart analyzing behavioral learner segments.
    """
    title = "Behavioural Learner Segmentation Across Study Vectors"
    if df.empty:
        fig = go.Figure()
        return apply_business_theme(fig, title=title, x_title="Sessions per Week", y_title="Session Duration", unit="mins")

    chart_df = df.copy()
    sess_wk_col = next((c for c in ["sessions_per_week", "active_days_per_week"] if c in chart_df.columns), None)
    dur_col = next((c for c in ["average_session_duration", "duration_minutes", "avg_session_duration"] if c in chart_df.columns), None)
    risk_col = next((c for c in ["dropout_risk_level", "risk_tier"] if c in chart_df.columns), None)
    quiz_col = next((c for c in ["quiz_average", "score_percentage"] if c in chart_df.columns), None)

    if not sess_wk_col or not dur_col:
        fig = go.Figure()
        return apply_business_theme(fig, title=title, x_title="Sessions per Week", y_title="Session Duration", unit="mins")

    fig = px.scatter(
        chart_df,
        x=sess_wk_col,
        y=dur_col,
        color=risk_col,
        size=quiz_col if quiz_col else None,
        color_discrete_map=RISK_COLOR_MAP if risk_col in RISK_COLOR_MAP else None,
        color_discrete_sequence=COLOR_PALETTES["categorical"]
    )

    fig.update_traces(
        marker=dict(opacity=0.85, line=dict(width=1, color="white")),
        hovertemplate="<b>Sessions / Wk:</b> %{x:.1f}<br>" +
                      "<b>Avg Duration:</b> %{y:.1f} mins<extra></extra>"
    )

    return apply_business_theme(
        fig,
        title=title,
        x_title=sess_wk_col.replace("_", " ").title(),
        y_title=dur_col.replace("_", " ").title(),
        unit="mins"
    )


def plot_course_performance(df: pd.DataFrame) -> go.Figure:
    """
    Creates an interactive horizontal bar chart ranking course performance by completion rate.
    """
    title = "Course Performance & Completion Rate Rankings (%)"
    if df.empty:
        fig = go.Figure()
        return apply_business_theme(fig, title=title, x_title="Completion Rate", y_title="Course Title", unit="%")

    chart_df = df.copy()
    course_col = next((c for c in ["course_title", "course_id", "category"] if c in chart_df.columns), None)
    comp_col = next((c for c in ["completion_rate_pct", "completion_rate", "completed_count"] if c in chart_df.columns), None)

    if not course_col or not comp_col:
        fig = go.Figure()
        return apply_business_theme(fig, title=title, x_title="Completion Rate", y_title="Course Title", unit="%")

    chart_df = chart_df.sort_values(by=comp_col, ascending=True)

    fig = px.bar(
        chart_df,
        x=comp_col,
        y=course_col,
        orientation="h",
        color=comp_col,
        color_continuous_scale="Viridis",
        text=chart_df[comp_col].apply(lambda v: f"{v:.1f}%" if v <= 100 else f"{v:,.0f}")
    )

    fig.update_traces(
        hovertemplate="<b>Course:</b> %{y}<br>" +
                      f"<b>{comp_col.replace('_', ' ').title()}:</b> %{{x:.1f}}%<extra></extra>"
    )

    max_val = float(chart_df[comp_col].max()) if not chart_df[comp_col].empty else 100.0
    fig.update_xaxes(range=[0, max(max_val * 1.15, 100.0)])

    return apply_business_theme(
        fig,
        title=title,
        x_title=comp_col.replace("_", " ").title(),
        y_title=course_col.replace("_", " ").title(),
        unit="%"
    )


def plot_risk_distribution(df: pd.DataFrame) -> go.Figure:
    """
    Creates an interactive donut/bar chart displaying learner dropout risk distribution.
    """
    title = "Learner Dropout Risk Distribution & Retention Priorities"
    if df.empty:
        fig = go.Figure()
        return apply_business_theme(fig, title=title, x_title="Risk Level", y_title="Learner Count", unit="")

    chart_df = df.copy()
    risk_col = next((c for c in ["dropout_risk_level", "risk_level", "risk_tier"] if c in chart_df.columns), None)

    if risk_col in chart_df.columns:
        counts = chart_df[risk_col].value_counts().reset_index()
        counts.columns = ["risk_level", "count"]
    else:
        counts = pd.DataFrame({
            "risk_level": ["Low", "Moderate", "High", "Critical"],
            "count": [0, 0, 0, 0]
        })

    total = counts["count"].sum()
    counts["percentage"] = (counts["count"] / max(total, 1) * 100).round(1)

    fig = px.pie(
        counts,
        names="risk_level",
        values="count",
        hole=0.45,
        color="risk_level",
        color_discrete_map=RISK_COLOR_MAP
    )

    fig.update_traces(
        textinfo="label+percent",
        hovertemplate="<b>Risk Level:</b> %{label}<br>" +
                      "<b>Learner Count:</b> %{value:,.0f}<br>" +
                      "<b>Percentage:</b> %{percent}<extra></extra>"
    )

    return apply_business_theme(
        fig,
        title=title,
        x_title="",
        y_title="",
        unit=""
    )


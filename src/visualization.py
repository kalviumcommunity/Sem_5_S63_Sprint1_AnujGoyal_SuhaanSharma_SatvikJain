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

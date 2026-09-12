"""
Reusable UI Components for the Streamlit Dashboard.

Provides standardized Streamlit components for headers, metric cards,
executive KPI summary grids, and Plotly chart rendering.
"""

from typing import Dict, Any, Optional
import streamlit as st
from dashboard.utils import format_kpi_summary


def render_header(title: str, subtitle: str) -> None:
    """Renders a standard application header."""
    st.title(title)
    st.caption(subtitle)
    st.divider()


def render_kpi_card(
    title: str,
    value: str,
    delta: Optional[str] = None,
    delta_color: str = "normal",
    help_text: Optional[str] = None
) -> None:
    """
    Renders a standard KPI metric card with optional delta change and help tooltip.

    Args:
        title: Metric label
        value: Formatted display string (e.g. '68.4%', '1,250')
        delta: Optional change indicator string (e.g. '+3.2%')
        delta_color: Color direction ('normal', 'inverse', 'off')
        help_text: Optional tooltip explanation text
    """
    st.metric(
        label=title,
        value=value,
        delta=delta,
        delta_color=delta_color,
        help=help_text
    )


def render_kpi_summary_grid(
    kpi_dict: Optional[Dict[str, Any]] = None,
    columns: int = 6
) -> Dict[str, Dict[str, Any]]:
    """
    Renders a responsive Streamlit grid of KPI summary metric cards displaying:
    1. Completion Rate
    2. Dropout Rate
    3. Active Learners
    4. At-Risk Learners
    5. Average Quiz Score
    6. Average Session Duration

    Args:
        kpi_dict: Raw KPI dictionary (or empty to use formatted defaults)
        columns: Number of grid columns (defaults to 6 for standard desktop view)

    Returns:
        Formatted KPI summary dictionary used for rendering.
    """
    summary = format_kpi_summary(kpi_dict or {})
    cols = st.columns(columns)
    metrics_list = list(summary.values())

    for idx, card in enumerate(metrics_list):
        col_target = cols[idx % columns]
        with col_target:
            render_kpi_card(
                title=card["label"],
                value=card["value"],
                delta=card.get("delta"),
                delta_color=card.get("delta_color", "normal"),
                help_text=card.get("help_text")
            )

    return summary


def render_chart(fig, use_container_width: bool = True) -> None:
    """Renders a standardized Plotly chart object in Streamlit dashboard."""
    st.plotly_chart(fig, use_container_width=use_container_width)


def render_insight_narrative(narrative: Any) -> None:
    """
    Renders a structured 4-stage analytical insight narrative card in Streamlit:
    Observation -> Interpretation -> Business Impact -> Suggested Action
    """
    if hasattr(narrative, "to_dict"):
        data = narrative.to_dict()
    elif isinstance(narrative, dict):
        data = narrative
    else:
        st.warning("Invalid narrative format.")
        return

    title = data.get("title", "Analytical Insight Narrative")
    domain = data.get("domain", "").upper()

    with st.expander(f"💡 [{domain}] {title}", expanded=True):
        st.markdown(f"**🔍 Observation:** {data.get('observation', '')}")
        st.markdown(f"**🧠 Interpretation:** {data.get('interpretation', '')}")
        st.markdown(f"**📈 Business Impact:** {data.get('business_impact', '')}")
        st.info(f"**🎯 Suggested Action:** {data.get('suggested_action', '')}")


def render_export_download_section(
    kpi_dict: Optional[Dict[str, Any]] = None,
    risk_df: Optional[Any] = None,
    course_df: Optional[Any] = None,
    behaviour_df: Optional[Any] = None,
    report_markdown: Optional[str] = None
) -> None:
    """
    Renders reusable Streamlit download buttons for exporting analytical outputs:
    - KPIs (CSV)
    - Learner Risk Data (CSV)
    - Course Metrics (CSV)
    - Behavioural Segments (CSV)
    - Executive Summary Report (Markdown)
    """
    import pandas as pd
    from src.export import (
        get_dataframe_csv_bytes,
        get_markdown_report_bytes
    )

    st.subheader("📥 Export Analytical Outputs & Reports")
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        if kpi_dict:
            kpi_df = pd.DataFrame([kpi_dict])
            st.download_button(
                label="KPIs (CSV)",
                data=get_dataframe_csv_bytes(kpi_df),
                file_name="kpi_summary.csv",
                mime="text/csv"
            )

    with col2:
        if risk_df is not None and not risk_df.empty:
            st.download_button(
                label="Risk Data (CSV)",
                data=get_dataframe_csv_bytes(risk_df),
                file_name="learner_risk_data.csv",
                mime="text/csv"
            )

    with col3:
        if course_df is not None and not course_df.empty:
            st.download_button(
                label="Course Metrics (CSV)",
                data=get_dataframe_csv_bytes(course_df),
                file_name="course_metrics.csv",
                mime="text/csv"
            )

    with col4:
        if behaviour_df is not None and not behaviour_df.empty:
            st.download_button(
                label="Segments (CSV)",
                data=get_dataframe_csv_bytes(behaviour_df),
                file_name="behavioural_segments.csv",
                mime="text/csv"
            )

    with col5:
        if report_markdown:
            st.download_button(
                label="Executive Report (MD)",
                data=get_markdown_report_bytes(report_markdown),
                file_name="executive_report.md",
                mime="text/markdown"
            )



"""
Reusable UI Components for the Streamlit Dashboard.

Provides standardized Streamlit components for headers, metric cards,
executive KPI summary grids, and Plotly chart rendering.
"""

from typing import Dict, Any, Optional
import streamlit as st
from dashboard.utils import format_kpi_summary
from dashboard.alerts import CRITICAL, NORMAL, WARNING, MetricAlert, overall_alert_status
from dashboard.sharing import DeliveryResult, PeriodicSummary


def render_header(title: str, subtitle: str) -> None:
    """Renders a standard application header with engaging retro-boxy neo-brutalist styling."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Plus+Jakarta+Sans:wght@500;700;800&display=swap');

        /* App canvas & typography */
        .stApp, [data-testid="stAppViewContainer"], .main {
            background-color: #FDFBF7 !important;
            color: #18181B !important;
            font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif !important;
        }

        /* Retro Command Hero Banner */
        .retro-banner {
            background-color: #FFFFFF;
            border: 2.5px solid #18181B;
            border-radius: 4px;
            box-shadow: 4px 4px 0px #18181B;
            padding: 18px 24px;
            margin-bottom: 22px;
            position: relative;
        }
        .retro-badge-row {
            display: flex;
            gap: 8px;
            margin-bottom: 10px;
            align-items: center;
        }
        .retro-chip {
            background-color: #FEF08A;
            border: 1.5px solid #18181B;
            border-radius: 2px;
            box-shadow: 2px 2px 0px #18181B;
            color: #18181B;
            font-family: 'Space Mono', monospace;
            font-size: 0.72rem;
            font-weight: 700;
            padding: 2px 8px;
            letter-spacing: 0.05em;
            display: inline-block;
        }
        .retro-chip-live {
            background-color: #BBF7D0;
            border: 1.5px solid #18181B;
            border-radius: 2px;
            box-shadow: 2px 2px 0px #18181B;
            color: #14532D;
            font-family: 'Space Mono', monospace;
            font-size: 0.72rem;
            font-weight: 700;
            padding: 2px 8px;
            letter-spacing: 0.05em;
            display: inline-block;
        }
        .retro-title {
            font-size: 1.75rem;
            font-weight: 800;
            color: #18181B;
            margin: 0 0 4px 0;
            letter-spacing: -0.02em;
        }
        .retro-subtitle {
            font-size: 0.95rem;
            color: #52525B;
            margin: 0;
            font-weight: 500;
        }

        /* Retro Sidebar */
        [data-testid="stSidebar"], [data-testid="stSidebarContent"] {
            background-color: #F4EFE6 !important;
            border-right: 2.5px solid #18181B !important;
        }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
            color: #27272A !important;
            font-weight: 600 !important;
        }

        /* Metric Cards: Chunky, tactile, offset hard shadows */
        [data-testid="stMetric"] {
            background-color: #FFFFFF !important;
            border: 2.5px solid #18181B !important;
            border-radius: 4px !important;
            box-shadow: 4px 4px 0px #18181B !important;
            padding: 16px 20px !important;
            transition: transform 0.15s ease, box-shadow 0.15s ease !important;
        }
        [data-testid="stMetric"]:hover {
            transform: translate(-2px, -2px) !important;
            box-shadow: 6px 6px 0px #18181B !important;
        }
        [data-testid="stMetricLabel"] p {
            font-family: 'Space Mono', monospace !important;
            color: #52525B !important;
            font-size: 0.8rem !important;
            font-weight: 700 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.04em !important;
        }
        [data-testid="stMetricValue"] {
            font-family: 'Space Mono', monospace !important;
            color: #18181B !important;
            font-weight: 700 !important;
            font-size: 1.85rem !important;
        }

        /* Buttons & Download buttons: Tactile mechanical press feel */
        .stButton > button, [data-testid="stDownloadButton"] > button {
            background-color: #FFFFFF !important;
            color: #18181B !important;
            border: 2.5px solid #18181B !important;
            border-radius: 4px !important;
            box-shadow: 3.5px 3.5px 0px #18181B !important;
            font-family: 'Space Mono', monospace !important;
            font-weight: 700 !important;
            font-size: 0.88rem !important;
            padding: 8px 18px !important;
            transition: all 0.1s ease !important;
        }
        .stButton > button:hover, [data-testid="stDownloadButton"] > button:hover {
            background-color: #FEF08A !important;
            color: #18181B !important;
            transform: translate(-1.5px, -1.5px) !important;
            box-shadow: 5px 5px 0px #18181B !important;
        }
        .stButton > button:active, [data-testid="stDownloadButton"] > button:active {
            transform: translate(2px, 2px) !important;
            box-shadow: 1px 1px 0px #18181B !important;
        }

        /* Form Inputs & Selectboxes */
        [data-baseweb="select"] > div, .stTextInput > div > div > input, .stMultiSelect {
            background-color: #FFFFFF !important;
            border: 2px solid #18181B !important;
            border-radius: 4px !important;
            box-shadow: 2px 2px 0px #18181B !important;
            color: #18181B !important;
        }

        /* Radio Options */
        [data-testid="stRadio"] label {
            font-family: 'Space Mono', monospace !important;
            font-size: 0.88rem !important;
            font-weight: 600 !important;
            color: #18181B !important;
        }

        /* Plotly Chart Card Framing */
        [data-testid="stPlotlyChart"] {
            background-color: #FFFFFF !important;
            border: 2.5px solid #18181B !important;
            border-radius: 4px !important;
            box-shadow: 4px 4px 0px #18181B !important;
            padding: 10px !important;
            margin-bottom: 20px !important;
        }

        /* Tables & DataFrames */
        [data-testid="stDataFrame"], [data-testid="stTable"] {
            border: 2.5px solid #18181B !important;
            border-radius: 4px !important;
            box-shadow: 3.5px 3.5px 0px #18181B !important;
            background-color: #FFFFFF !important;
        }

        /* Expanders & Accordions */
        [data-testid="stExpander"] {
            background-color: #FFFFFF !important;
            border: 2px solid #18181B !important;
            border-radius: 4px !important;
            box-shadow: 3px 3px 0px #18181B !important;
        }

        /* Alert Notification Banners */
        .stAlert {
            border: 2px solid #18181B !important;
            border-radius: 4px !important;
            box-shadow: 3px 3px 0px #18181B !important;
            font-weight: 600 !important;
        }

        /* Headings */
        h1, h2, h3, h4, h5, h6 {
            color: #18181B !important;
            font-weight: 800 !important;
            letter-spacing: -0.01em !important;
        }

        /* Dashed retro dividers */
        hr {
            border: none !important;
            border-top: 2px dashed #18181B !important;
            margin: 20px 0 !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.markdown(
        f"""
        <div class="retro-banner">
            <div class="retro-badge-row">
                <span class="retro-chip">⚡ EDTECH INTELLIGENCE</span>
                <span class="retro-chip-live">● SYSTEM ACTIVE</span>
                <span class="retro-chip">RETRO-BOX SPEC</span>
            </div>
            <div class="retro-title">{title}</div>
            <div class="retro-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


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
    columns: int = 4
) -> Dict[str, Dict[str, Any]]:
    """
    Renders a responsive Streamlit grid of KPI summary metric cards displaying:
    Eight filtered dashboard KPI cards.

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


def render_alert_panel(alerts: list[MetricAlert]) -> None:
    """Render threshold results with clear severity and business explanations."""
    status = overall_alert_status(alerts)
    st.subheader(f"Metric Monitoring: {status}")
    for alert in alerts:
        message = f"{alert.metric}: {alert.explanation}"
        if alert.status == CRITICAL:
            st.error(f"{alert.status} | {message}")
        elif alert.status == WARNING:
            st.warning(f"{alert.status} | {message}")
        else:
            st.success(f"{alert.status} | {message}")


def render_report_sharing(summary: PeriodicSummary, sender: Any) -> None:
    """Render optional report preview and email delivery controls."""
    st.subheader("Share Periodic Analytics Summary")
    st.markdown(summary.markdown)
    recipient = st.text_input("Recipient email", key="report_recipient_email")
    if st.button("Send summary email", key="send_summary_email"):
        result: DeliveryResult = sender.send(recipient, summary)
        if result.status == "SENT":
            st.success(result.message)
        elif result.status == "NOT_CONFIGURED":
            st.info(result.message)
        else:
            st.error(result.message)


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



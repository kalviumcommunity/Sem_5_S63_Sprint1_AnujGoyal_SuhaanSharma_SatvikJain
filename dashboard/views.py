"""
Streamlit Page Views for Learning Analytics Intelligence Platform.

Contains view handler functions for the dashboard navigation pages:
1. Overview
2. Student Behaviour
3. Course Analytics
4. Dropout Risk
5. Behaviour Trends
6. SQL Insights
7. Reports
"""

from typing import Optional, Any
import streamlit as st
import pandas as pd
from dashboard.components import (
    render_kpi_summary_grid,
    render_chart,
    render_insight_narrative,
    render_export_download_section
)
from src.analysis import (
    get_business_kpis,
    run_data_storytelling_analysis,
    run_executive_reporting_analysis
)
from src.visualization import (
    plot_completion_vs_dropout,
    plot_session_trends,
    plot_quiz_performance,
    plot_engagement,
    plot_behavioural_segments,
    plot_course_performance,
    plot_risk_distribution
)
from src.database import execute_analytical_views
from dashboard.filters import DashboardFilters, calculate_filtered_kpis
from dashboard.utils import load_uploaded_dataset


def _resolve_views(db_path: Any, views: Optional[dict]) -> dict:
    """Use the app's shared view bundle or load one for direct view calls."""
    if views is not None:
        return views
    try:
        return execute_analytical_views(db_path=db_path)
    except Exception:
        return {}


def view_overview(
    db_path: Any = None,
    views: Optional[dict] = None,
    filters: Optional[DashboardFilters] = None,
) -> None:
    """Renders the Overview page view."""
    st.header("📌 Platform Performance Overview")
    st.caption("High-level KPI scorecard and macro cohort analysis.")

    views = _resolve_views(db_path, views)
    kpi_data = calculate_filtered_kpis(views) if filters is not None else get_business_kpis(db_path=db_path)

    render_kpi_summary_grid(kpi_data, columns=6)
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        student_df = views.get("student_engagement_view", pd.DataFrame())
        fig_comp = plot_completion_vs_dropout(student_df)
        render_chart(fig_comp)

    with col2:
        try:
            risk_df = views.get("dropout_risk_view", pd.DataFrame()) if 'views' in locals() else pd.DataFrame()
        except Exception:
            risk_df = pd.DataFrame()
        fig_risk = plot_risk_distribution(risk_df)
        render_chart(fig_risk)


def view_student_behaviour(
    db_path: Any = None,
    views: Optional[dict] = None,
    filters: Optional[DashboardFilters] = None,
) -> None:
    """Renders the Student Behaviour page view."""
    st.header("🎓 Learner Engagement & Behavioural Segmentation")
    st.caption("Investigating how student session habits and consistency impact progress.")

    views = _resolve_views(db_path, views)
    behaviour_df = views.get("student_engagement_view", pd.DataFrame())

    col1, col2 = st.columns(2)
    with col1:
        fig_eng = plot_engagement(behaviour_df)
        render_chart(fig_eng)

    with col2:
        fig_seg = plot_behavioural_segments(behaviour_df)
        render_chart(fig_seg)

    try:
        narratives = run_data_storytelling_analysis(db_path=db_path)
        if "engagement" in narratives:
            render_insight_narrative(narratives["engagement"])
    except Exception:
        pass


def view_course_analytics(
    db_path: Any = None,
    views: Optional[dict] = None,
    filters: Optional[DashboardFilters] = None,
) -> None:
    """Renders the Course Analytics page view."""
    st.header("📚 Course Performance & Quiz Mastery Analytics")
    st.caption("Comparing completion rates and quiz score distributions across subjects.")

    views = _resolve_views(db_path, views)
    course_df = views.get("course_performance_view", pd.DataFrame())

    col1, col2 = st.columns(2)
    with col1:
        fig_course = plot_course_performance(course_df)
        render_chart(fig_course)

    with col2:
        fig_quiz = plot_quiz_performance(course_df)
        render_chart(fig_quiz)

    try:
        narratives = run_data_storytelling_analysis(db_path=db_path)
        if "course_performance" in narratives:
            render_insight_narrative(narratives["course_performance"])
    except Exception:
        pass


def view_dropout_risk(
    db_path: Any = None,
    views: Optional[dict] = None,
    filters: Optional[DashboardFilters] = None,
) -> None:
    """Renders the Dropout Risk page view."""
    st.header("⚠️ Early Risk Detection & Retention Diagnostics")
    st.caption("Identifying vulnerable student cohorts before silent drop-off occurs.")

    views = _resolve_views(db_path, views)
    risk_df = views.get("dropout_risk_view", pd.DataFrame())

    col1, col2 = st.columns(2)
    with col1:
        fig_risk = plot_risk_distribution(risk_df)
        render_chart(fig_risk)

    with col2:
        st.subheader("High / Critical Risk Cohort Diagnostics")
        if not risk_df.empty:
            at_risk_df = risk_df[risk_df["is_at_risk"] == 1] if "is_at_risk" in risk_df.columns else risk_df
            st.dataframe(at_risk_df.head(10), use_container_width=True)
        else:
            st.info("No risk records currently loaded.")

    try:
        narratives = run_data_storytelling_analysis(db_path=db_path)
        if "dropout" in narratives:
            render_insight_narrative(narratives["dropout"])
        if "risk" in narratives:
            render_insight_narrative(narratives["risk"])
    except Exception:
        pass


def view_behaviour_trends(
    db_path: Any = None,
    views: Optional[dict] = None,
    filters: Optional[DashboardFilters] = None,
) -> None:
    """Renders the Behaviour Trends page view."""
    st.header("📈 Temporal Activity & Engagement Trends")
    st.caption("Tracking weekly study duration, session frequency, and velocity over time.")

    views = _resolve_views(db_path, views)
    weekly_df = views.get("weekly_activity_view", pd.DataFrame())

    fig_trend = plot_session_trends(weekly_df)
    render_chart(fig_trend)

    if not weekly_df.empty:
        st.subheader("Weekly Activity Summary Table")
        st.dataframe(weekly_df, use_container_width=True)


def view_sql_insights(
    db_path: Any = None,
    views: Optional[dict] = None,
    filters: Optional[DashboardFilters] = None,
) -> None:
    """Renders the SQL Insights page view."""
    st.header("⚡ SQL Analytical Views & Query Intelligence")
    st.caption("Exploring SQLite database views, multi-table joins, and aggregation layers.")

    views = _resolve_views(db_path, views)

    selected_view = st.selectbox(
        "Select Analytical Database View",
        list(views.keys()) if views else ["No views loaded"]
    )

    if selected_view in views and not views[selected_view].empty:
        st.dataframe(views[selected_view], use_container_width=True)
        st.caption(f"Loaded {len(views[selected_view])} records from '{selected_view}'.")
    else:
        st.info(f"View '{selected_view}' returned 0 rows or is uninitialized.")


def view_reports(
    db_path: Any = None,
    views: Optional[dict] = None,
    filters: Optional[DashboardFilters] = None,
) -> None:
    """Renders the Reports page view."""
    st.header("📑 Executive Briefing & Multi-Format Exports")
    st.caption("Access non-technical executive briefs and export analytical output packages.")

    try:
        report_data = run_executive_reporting_analysis(db_path=db_path)
        from src.reporting import build_executive_report_markdown
        report_md = build_executive_report_markdown(report_data)
    except Exception:
        report_data = {}
        report_md = "# Executive Report\n\nReport data loading..."

    st.markdown(report_md)
    st.divider()

    views = _resolve_views(db_path, views)
    kpis = calculate_filtered_kpis(views) if filters is not None else get_business_kpis(db_path=db_path)

    render_export_download_section(
        kpi_dict=kpis,
        risk_df=views.get("dropout_risk_view"),
        course_df=views.get("course_performance_view"),
        behaviour_df=views.get("student_engagement_view"),
        report_markdown=report_md
    )


def view_dataset_upload() -> None:
    """Renders the CSV/JSON upload and dataset preview page."""
    st.header("Dataset Upload & Preview")
    st.caption("Inspect a dataset before using it in the learning analytics workflow.")

    uploaded_file = st.file_uploader(
        "Upload a CSV or JSON dataset",
        type=["csv", "json"],
        accept_multiple_files=False,
    )
    if uploaded_file is None:
        st.info("Upload a CSV or JSON file to preview its structure.")
        return

    dataframe, validation_result = load_uploaded_dataset(uploaded_file)
    if not validation_result.is_valid:
        st.error(f"Upload validation failed for '{uploaded_file.name}'.")
        for error in validation_result.errors:
            st.write(f"- {error}")
        return

    st.success(f"'{uploaded_file.name}' passed validation.")
    metric_columns = st.columns(2)
    metric_columns[0].metric("Rows", f"{validation_result.row_count:,}")
    metric_columns[1].metric("Columns", f"{validation_result.column_count:,}")

    st.subheader("Preview")
    st.dataframe(dataframe.head(10), use_container_width=True)

    type_summary = pd.DataFrame({
        "column": dataframe.columns,
        "data_type": dataframe.dtypes.astype(str).values,
    })
    missing_summary = pd.DataFrame({
        "column": dataframe.columns,
        "missing_values": dataframe.isna().sum().values,
    })
    summary_columns = st.columns(2)
    with summary_columns[0]:
        st.subheader("Data Types")
        st.dataframe(type_summary, hide_index=True, use_container_width=True)
    with summary_columns[1]:
        st.subheader("Missing Values")
        st.dataframe(missing_summary, hide_index=True, use_container_width=True)

"""Shared dashboard filter state, widgets, and filtered analytical views."""

from dataclasses import dataclass, field
from datetime import date
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import streamlit as st

from dashboard.state import (
    FILTER_KEYS,
    initialize_session_state,
    save_filter_snapshot,
    sync_filter_options,
)


@dataclass
class DashboardFilters:
    """Selections applied consistently to all learner-level dashboard views."""

    courses: List[str] = field(default_factory=list)
    date_range: Optional[Tuple[date, date]] = None
    completion_statuses: List[str] = field(default_factory=list)
    risk_levels: List[str] = field(default_factory=list)
    learner_segments: List[str] = field(default_factory=list)
    minimum_quiz_score: float = 0.0


def learner_segment(series: pd.Series) -> pd.Series:
    """Classify engagement scores into stable learner segments."""
    scores = pd.to_numeric(series, errors="coerce").fillna(0.0)
    return pd.cut(
        scores,
        bins=[-float("inf"), 40.0, 70.0, float("inf")],
        labels=["Low Engagement", "Moderate Engagement", "High Engagement"],
    ).astype(str)


def _option_values(dataframe: pd.DataFrame, columns: List[str]) -> List[str]:
    for column in columns:
        if column in dataframe.columns:
            return sorted(dataframe[column].dropna().astype(str).unique().tolist())
    return []


def _date_bounds(dataframe: pd.DataFrame) -> Optional[Tuple[date, date]]:
    for column in ["registration_date", "session_start", "activity_week"]:
        if column in dataframe.columns:
            dates = pd.to_datetime(dataframe[column], errors="coerce").dropna()
            if not dates.empty:
                return dates.min().date(), dates.max().date()
    return None


def _learner_dataframe(views: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    return views.get("student_engagement_view", pd.DataFrame())


def render_filter_sidebar(views: Dict[str, pd.DataFrame]) -> DashboardFilters:
    """Render shared sidebar widgets and return their current selections."""
    initialize_session_state()
    dataframe = _learner_dataframe(views)
    st.sidebar.subheader("Dashboard Filters")

    courses = _option_values(dataframe, ["course_title", "target_course_id", "course_id"])
    statuses = _option_values(dataframe, ["completion_status"])
    risks = _option_values(dataframe, ["dropout_risk_level", "risk_level", "risk_tier"])
    segments = ["Low Engagement", "Moderate Engagement", "High Engagement"]
    sync_filter_options(
        options={
            "courses": courses,
            "completion_statuses": statuses,
            "risk_levels": risks,
            "learner_segments": segments,
        },
        date_bounds=_date_bounds(dataframe),
    )

    selected_courses = st.sidebar.multiselect("Course", courses, key=FILTER_KEYS["courses"])

    bounds = _date_bounds(dataframe)
    selected_dates = None
    if bounds:
        selected_dates = st.sidebar.date_input(
            "Registration date range",
            min_value=bounds[0],
            max_value=bounds[1],
            key=FILTER_KEYS["date_range"],
        )
        if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:
            selected_dates = (selected_dates[0], selected_dates[1])
        else:
            selected_dates = None

    selected_statuses = st.sidebar.multiselect(
        "Completion status", statuses, key=FILTER_KEYS["completion_statuses"]
    )
    selected_risks = st.sidebar.multiselect("Risk level", risks, key=FILTER_KEYS["risk_levels"])
    selected_segments = st.sidebar.multiselect(
        "Learner segment", segments, key=FILTER_KEYS["learner_segments"]
    )

    selected_quiz_score = st.sidebar.slider(
        "Minimum quiz performance (%)",
        min_value=0.0,
        max_value=100.0,
        step=1.0,
        key=FILTER_KEYS["minimum_quiz_score"],
    )

    filters = DashboardFilters(
        courses=selected_courses,
        date_range=selected_dates,
        completion_statuses=selected_statuses,
        risk_levels=selected_risks,
        learner_segments=selected_segments,
        minimum_quiz_score=selected_quiz_score,
    )
    save_filter_snapshot(filters)
    return filters


def _filter_by_values(dataframe: pd.DataFrame, columns: List[str], values: List[str]) -> pd.DataFrame:
    if not values:
        return dataframe.iloc[0:0]
    for column in columns:
        if column in dataframe.columns:
            return dataframe[dataframe[column].astype(str).isin(values)]
    return dataframe


def filter_dataframe(dataframe: pd.DataFrame, filters: DashboardFilters) -> pd.DataFrame:
    """Apply the shared filter state to any compatible analytical DataFrame."""
    if dataframe is None or dataframe.empty:
        return dataframe.copy() if dataframe is not None else pd.DataFrame()

    filtered = dataframe.copy()
    filtered = _filter_by_values(filtered, ["course_title", "target_course_id", "course_id"], filters.courses)
    filtered = _filter_by_values(filtered, ["completion_status"], filters.completion_statuses)
    filtered = _filter_by_values(filtered, ["dropout_risk_level", "risk_level", "risk_tier"], filters.risk_levels)

    if filters.learner_segments:
        segment_column = next((column for column in ["learner_segment", "segment"] if column in filtered.columns), None)
        if segment_column:
            segments = filtered[segment_column].astype(str)
            filtered = filtered[segments.isin(filters.learner_segments)]
        elif "engagement_score" in filtered.columns:
            segments = learner_segment(filtered["engagement_score"])
            filtered = filtered[segments.isin(filters.learner_segments)]
    else:
        filtered = filtered.iloc[0:0]

    if filters.minimum_quiz_score > 0:
        quiz_column = next((column for column in ["quiz_average", "avg_quiz_score", "score_percentage"] if column in filtered.columns), None)
        if quiz_column:
            filtered = filtered[pd.to_numeric(filtered[quiz_column], errors="coerce").fillna(0) >= filters.minimum_quiz_score]

    if filters.date_range:
        date_column = next((column for column in ["registration_date", "session_start", "activity_week"] if column in filtered.columns), None)
        if date_column:
            dates = pd.to_datetime(filtered[date_column], errors="coerce").dt.date
            filtered = filtered[dates.between(filters.date_range[0], filters.date_range[1])]

    return filtered


def _build_course_performance(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Re-aggregate course metrics from the filtered learner-level view."""
    if dataframe.empty:
        return pd.DataFrame()

    group_columns = [column for column in ["target_course_id", "course_title", "category"] if column in dataframe.columns]
    if not group_columns:
        return pd.DataFrame()

    grouped = dataframe.groupby(group_columns, dropna=False)
    result = grouped.size().rename("total_enrolled").reset_index()
    result["completed_count"] = grouped["completion_status"].apply(
        lambda values: values.astype(str).str.lower().eq("completed").sum()
    ).to_numpy() if "completion_status" in dataframe.columns else 0
    result["dropped_count"] = grouped["completion_status"].apply(
        lambda values: values.astype(str).str.lower().eq("dropped").sum()
    ).to_numpy() if "completion_status" in dataframe.columns else 0
    result["completion_rate_pct"] = (result["completed_count"] / result["total_enrolled"] * 100).round(2)
    for source, target in [
        ("engagement_score", "avg_engagement_score"),
        ("course_progress", "avg_course_progress"),
        ("quiz_average", "avg_quiz_score"),
    ]:
        result[target] = grouped[source].mean().round(2).to_numpy() if source in dataframe.columns else 0.0
    result = result.rename(columns={"target_course_id": "course_id"})
    return result


def filter_dashboard_views(views: Dict[str, pd.DataFrame], filters: DashboardFilters) -> Dict[str, pd.DataFrame]:
    """Return all analytical views after applying one shared filter state."""
    filtered_views = {name: filter_dataframe(dataframe, filters) for name, dataframe in views.items()}
    learners = filtered_views.get("student_engagement_view", pd.DataFrame())
    filtered_views["course_performance_view"] = _build_course_performance(learners)
    return filtered_views


def calculate_filtered_kpis(views: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """Calculate KPI cards from the same filtered learner view as the charts."""
    dataframe = views.get("student_engagement_view", pd.DataFrame())
    if dataframe.empty:
        return {
            "total_students": 0,
            "completion_rate_pct": 0.0,
            "dropout_rate_pct": 0.0,
            "active_learner_count": 0,
            "avg_quiz_score_pct": 0.0,
            "avg_session_duration_minutes": 0.0,
            "at_risk_learner_count": 0,
        }

    total = len(dataframe)
    statuses = dataframe.get("completion_status", pd.Series(index=dataframe.index, dtype=str)).astype(str).str.lower()
    quiz_scores = pd.to_numeric(dataframe.get("quiz_average", 0), errors="coerce")
    session_duration = pd.to_numeric(dataframe.get("avg_session_duration", 0), errors="coerce")
    risk = dataframe.get("dropout_risk_level", pd.Series(index=dataframe.index, dtype=str)).astype(str).str.lower()
    return {
        "total_students": total,
        "completion_rate_pct": round(statuses.eq("completed").mean() * 100, 2),
        "dropout_rate_pct": round(statuses.eq("dropped").mean() * 100, 2),
        "active_learner_count": dataframe.get("student_id", pd.Series(dtype=str)).nunique(),
        "avg_quiz_score_pct": round(quiz_scores.mean(), 2),
        "avg_session_duration_minutes": round(session_duration.mean(), 2),
        "at_risk_learner_count": int(risk.isin(["high", "critical"]).sum()),
    }
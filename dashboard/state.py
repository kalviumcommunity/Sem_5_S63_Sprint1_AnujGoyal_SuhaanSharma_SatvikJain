"""Centralized Streamlit session-state keys and workflow persistence helpers."""

from hashlib import sha256
from typing import Any, Dict, MutableMapping, Optional, Tuple

import pandas as pd
import streamlit as st

from src.validation import ValidationResult


PAGE_KEY = "dashboard_page"
FILTER_SNAPSHOT_KEY = "dashboard_filters"
FILTER_OPTIONS_KEY = "dashboard_filter_options"
FILTER_DATE_BOUNDS_KEY = "dashboard_filter_date_bounds"
UPLOAD_WIDGET_KEY = "dashboard_upload_widget"
UPLOAD_DATASET_KEY = "dashboard_uploaded_dataset"
UPLOAD_FILENAME_KEY = "dashboard_uploaded_filename"
UPLOAD_VALIDATION_KEY = "dashboard_upload_validation"
UPLOAD_SIGNATURE_KEY = "dashboard_upload_signature"

FILTER_KEYS = {
    "courses": "dashboard_filter_courses",
    "date_range": "dashboard_filter_date_range",
    "completion_statuses": "dashboard_filter_completion_statuses",
    "risk_levels": "dashboard_filter_risk_levels",
    "learner_segments": "dashboard_filter_learner_segments",
    "engagement_levels": "dashboard_filter_engagement_levels",
    "quiz_score_range": "dashboard_filter_quiz_score_range",
    "minimum_quiz_score": "dashboard_filter_minimum_quiz_score",
}


def _state(session_state: Optional[MutableMapping[str, Any]] = None) -> MutableMapping[str, Any]:
    return session_state if session_state is not None else st.session_state


def initialize_session_state(session_state: Optional[MutableMapping[str, Any]] = None) -> None:
    """Create stable defaults once for navigation, filters, and uploads."""
    state = _state(session_state)
    defaults = {
        PAGE_KEY: "Overview",
        FILTER_SNAPSHOT_KEY: None,
        FILTER_OPTIONS_KEY: {},
        FILTER_DATE_BOUNDS_KEY: None,
        UPLOAD_DATASET_KEY: None,
        UPLOAD_FILENAME_KEY: None,
        UPLOAD_VALIDATION_KEY: None,
        UPLOAD_SIGNATURE_KEY: None,
        FILTER_KEYS["courses"]: [],
        FILTER_KEYS["date_range"]: None,
        FILTER_KEYS["completion_statuses"]: [],
        FILTER_KEYS["risk_levels"]: [],
        FILTER_KEYS["learner_segments"]: [],
        FILTER_KEYS["engagement_levels"]: [],
        FILTER_KEYS["quiz_score_range"]: (0.0, 100.0),
        FILTER_KEYS["minimum_quiz_score"]: 0.0,
    }
    for key, value in defaults.items():
        state.setdefault(key, value)


def sync_filter_options(
    options: Dict[str, list],
    date_bounds: Optional[Tuple[Any, Any]],
    session_state: Optional[MutableMapping[str, Any]] = None,
) -> None:
    """Preserve valid selections while adapting state to the current dataset."""
    state = _state(session_state)
    initialize_session_state(state)
    previous_options = state[FILTER_OPTIONS_KEY]

    for name in [
        "courses",
        "completion_statuses",
        "risk_levels",
        "learner_segments",
        "engagement_levels",
    ]:
        key = FILTER_KEYS[name]
        available = options.get(name, [])
        current = state[key]
        state[key] = [value for value in current if value in available]
        previous_options[name] = list(available)

    if date_bounds:
        current_range = state[FILTER_KEYS["date_range"]]
        previous_bounds = state[FILTER_DATE_BOUNDS_KEY]
        if not isinstance(current_range, (tuple, list)) or len(current_range) != 2 or previous_bounds is None:
            state[FILTER_KEYS["date_range"]] = date_bounds
        else:
            start = max(date_bounds[0], min(current_range[0], date_bounds[1]))
            end = min(date_bounds[1], max(current_range[1], date_bounds[0]))
            state[FILTER_KEYS["date_range"]] = (min(start, end), max(start, end))
        state[FILTER_DATE_BOUNDS_KEY] = date_bounds
    else:
        state[FILTER_KEYS["date_range"]] = None
        state[FILTER_DATE_BOUNDS_KEY] = None


def save_filter_snapshot(filters: Any, session_state: Optional[MutableMapping[str, Any]] = None) -> None:
    """Store the normalized filter object for downstream workflow steps."""
    _state(session_state)[FILTER_SNAPSHOT_KEY] = filters


def upload_signature(uploaded_file: Any) -> str:
    """Return a stable content signature so uploads are parsed only when changed."""
    return sha256(uploaded_file.getvalue()).hexdigest()


def store_uploaded_dataset(
    dataframe: pd.DataFrame,
    filename: str,
    validation: ValidationResult,
    signature: str,
    session_state: Optional[MutableMapping[str, Any]] = None,
) -> None:
    """Persist the latest uploaded dataset and its validation result."""
    state = _state(session_state)
    state[UPLOAD_DATASET_KEY] = dataframe
    state[UPLOAD_FILENAME_KEY] = filename
    state[UPLOAD_VALIDATION_KEY] = validation
    state[UPLOAD_SIGNATURE_KEY] = signature


def get_uploaded_dataset(
    session_state: Optional[MutableMapping[str, Any]] = None,
) -> Tuple[Optional[pd.DataFrame], Optional[str], Optional[ValidationResult]]:
    """Return the persisted upload workflow state."""
    state = _state(session_state)
    return (
        state.get(UPLOAD_DATASET_KEY),
        state.get(UPLOAD_FILENAME_KEY),
        state.get(UPLOAD_VALIDATION_KEY),
    )


def clear_uploaded_dataset(session_state: Optional[MutableMapping[str, Any]] = None) -> None:
    """Clear persisted upload state while leaving filters and navigation intact."""
    state = _state(session_state)
    state[UPLOAD_DATASET_KEY] = None
    state[UPLOAD_FILENAME_KEY] = None
    state[UPLOAD_VALIDATION_KEY] = None
    state[UPLOAD_SIGNATURE_KEY] = None
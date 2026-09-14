"""Tests for centralized dashboard session-state persistence helpers."""

from datetime import date

import pandas as pd

from dashboard.state import (
    FILTER_KEYS,
    UPLOAD_DATASET_KEY,
    UPLOAD_FILENAME_KEY,
    UPLOAD_SIGNATURE_KEY,
    UPLOAD_VALIDATION_KEY,
    clear_uploaded_dataset,
    get_uploaded_dataset,
    initialize_session_state,
    store_uploaded_dataset,
    sync_filter_options,
)
from src.validation import ValidationResult


def test_initialize_session_state_is_idempotent():
    state = {}
    initialize_session_state(state)
    state[FILTER_KEYS["courses"]] = ["Python"]

    initialize_session_state(state)

    assert state[FILTER_KEYS["courses"]] == ["Python"]


def test_sync_filter_options_preserves_valid_choices_and_prunes_removed_values():
    state = {}
    initialize_session_state(state)
    sync_filter_options(
        {"courses": ["Python", "SQL"], "completion_statuses": ["Completed"]},
        (date(2026, 1, 1), date(2026, 2, 28)),
        state,
    )
    state[FILTER_KEYS["courses"]] = ["Python", "Removed"]
    state[FILTER_KEYS["date_range"]] = (date(2026, 1, 5), date(2026, 3, 1))

    sync_filter_options(
        {"courses": ["Python", "SQL"]},
        (date(2026, 1, 1), date(2026, 2, 28)),
        state,
    )

    assert state[FILTER_KEYS["courses"]] == ["Python"]
    assert state[FILTER_KEYS["date_range"]] == (date(2026, 1, 5), date(2026, 2, 28))


def test_uploaded_dataset_state_round_trip_and_clear():
    state = {}
    dataframe = pd.DataFrame({"student_id": ["S001"]})
    validation = ValidationResult(is_valid=True, dataset_name="students.csv", row_count=1, column_count=1)

    store_uploaded_dataset(dataframe, "students.csv", validation, "signature", state)
    stored_dataframe, filename, stored_validation = get_uploaded_dataset(state)

    assert stored_dataframe.equals(dataframe)
    assert filename == "students.csv"
    assert stored_validation.is_valid is True
    assert state[UPLOAD_DATASET_KEY] is stored_dataframe
    assert state[UPLOAD_FILENAME_KEY] == filename
    assert state[UPLOAD_VALIDATION_KEY] is stored_validation
    assert state[UPLOAD_SIGNATURE_KEY] == "signature"

    clear_uploaded_dataset(state)
    assert get_uploaded_dataset(state) == (None, None, None)
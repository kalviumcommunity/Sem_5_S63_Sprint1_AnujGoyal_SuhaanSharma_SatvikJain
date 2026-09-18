"""Tests for the Streamlit dataset upload and preview loader."""

from io import BytesIO

from dashboard.utils import load_uploaded_dataset


def uploaded_file(filename: str, content: str) -> BytesIO:
    """Create a small Streamlit UploadedFile-compatible test object."""
    file_object = BytesIO(content.encode("utf-8"))
    file_object.name = filename
    return file_object


def test_load_uploaded_csv_returns_data_and_summary():
    dataframe, result = load_uploaded_dataset(
        uploaded_file("activity.csv", "student_id,minutes\nS001,30\nS002,\n")
    )

    assert result.is_valid is True
    assert result.dataset_name == "activity.csv"
    assert result.row_count == 2
    assert result.column_count == 2
    assert dataframe.isna().sum()["minutes"] == 1


def test_load_uploaded_json_returns_data():
    dataframe, result = load_uploaded_dataset(
        uploaded_file("activity.json", '[{"student_id": "S001", "minutes": 30}]')
    )

    assert result.is_valid is True
    assert dataframe.to_dict(orient="records") == [{"student_id": "S001", "minutes": 30}]


def test_load_uploaded_empty_file_fails_source_validation():
    dataframe, result = load_uploaded_dataset(uploaded_file("empty.csv", ""))

    assert dataframe.empty
    assert result.is_valid is False
    assert any("0 bytes" in error for error in result.errors)


def test_load_uploaded_header_only_csv_fails_dataset_validation():
    dataframe, result = load_uploaded_dataset(
        uploaded_file("header-only.csv", "student_id,minutes\n")
    )

    assert dataframe.empty
    assert result.is_valid is False
    assert any("empty" in error.lower() for error in result.errors)


def test_load_uploaded_malformed_json_fails_with_clear_error():
    dataframe, result = load_uploaded_dataset(
        uploaded_file("broken.json", '{"student_id":')
    )

    assert dataframe.empty
    assert result.is_valid is False
    assert any("malformed" in error.lower() for error in result.errors)


def test_load_uploaded_unsupported_file_fails_source_validation():
    dataframe, result = load_uploaded_dataset(uploaded_file("activity.txt", "student_id\nS001\n"))

    assert dataframe.empty
    assert result.is_valid is False
    assert any("Unsupported file format" in error for error in result.errors)
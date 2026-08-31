"""
Unit tests for Concept #6: Dataset Profiling & Quality Assessment.
Tests structured profiling, missing values, duplicates, numerical statistics, and quality scorecards.
"""

import pytest
import pandas as pd
import numpy as np

from src.profiling import (
    profile_dataset,
    profile_all_datasets,
    generate_quality_scorecard,
    DatasetProfile
)
from src.workflow import DataWorkflow


@pytest.fixture
def sample_activity_df():
    """Provides a realistic student activity dataset with intentional nulls and duplicates."""
    return pd.DataFrame({
        "student_id": ["S001", "S002", "S003", "S004", "S004"],
        "course_id": ["C101", "C101", "C102", "C102", "C102"],
        "active_minutes": [45.0, 60.0, np.nan, 120.0, 120.0],
        "quiz_score": [85.0, 90.0, 70.0, 95.0, 95.0],
        "device": ["Mobile", "Desktop", "Desktop", "Mobile", "Mobile"]
    })


def test_profile_dataset_metrics(sample_activity_df):
    """Test standard dimensional and quality metrics in DatasetProfile."""
    profile = profile_dataset(sample_activity_df, dataset_name="Activity")

    assert isinstance(profile, DatasetProfile)
    assert profile.dataset_name == "Activity"
    assert profile.row_count == 5
    assert profile.column_count == 5
    assert profile.duplicate_count == 1
    assert profile.duplicate_percentage == 20.0
    assert profile.total_missing_cells == 1
    assert profile.completeness_percentage > 90.0
    assert 0.0 <= profile.quality_score <= 100.0
    assert profile.memory_usage_mb > 0.0


def test_profile_column_metadata(sample_activity_df):
    """Test column-level metadata extraction."""
    profile = profile_dataset(sample_activity_df, dataset_name="Activity")

    assert "student_id" in profile.column_profiles
    assert "active_minutes" in profile.column_profiles

    active_meta = profile.column_profiles["active_minutes"]
    assert active_meta["null_count"] == 1
    assert active_meta["null_percentage"] == 20.0
    assert active_meta["unique_count"] == 3


def test_profile_numerical_summary(sample_activity_df):
    """Test numerical statistics calculation (mean, std, min, 25%, 50%, 75%, max)."""
    profile = profile_dataset(sample_activity_df, dataset_name="Activity")

    assert "quiz_score" in profile.numerical_summary
    quiz_stats = profile.numerical_summary["quiz_score"]

    assert quiz_stats["count"] == 5.0
    assert quiz_stats["min"] == 70.0
    assert quiz_stats["max"] == 95.0
    assert quiz_stats["50% (median)"] == 90.0
    assert "mean" in quiz_stats
    assert "std" in quiz_stats


def test_profile_categorical_summary(sample_activity_df):
    """Test categorical summary extraction (unique_categories, mode, top_categories)."""
    profile = profile_dataset(sample_activity_df, dataset_name="Activity")

    assert "device" in profile.categorical_summary
    device_stats = profile.categorical_summary["device"]

    assert device_stats["unique_categories"] == 2
    assert device_stats["mode"] == "Mobile"
    assert "Mobile" in device_stats["top_categories"]


def test_profile_empty_dataframe():
    """Test profiling on empty DataFrames without exceptions."""
    empty_df = pd.DataFrame()
    profile = profile_dataset(empty_df, dataset_name="EmptyDataset")

    assert profile.row_count == 0
    assert profile.column_count == 0
    assert profile.completeness_percentage == 0.0
    assert profile.quality_score == 0.0
    assert profile.to_dict()["row_count"] == 0


def test_profile_dataframe_export_helpers(sample_activity_df):
    """Test converting profile results to DataFrames for Streamlit tables."""
    profile = profile_dataset(sample_activity_df, dataset_name="Activity")

    col_df = profile.to_column_summary_df()
    assert isinstance(col_df, pd.DataFrame)
    assert len(col_df) == 5
    assert "Column" in col_df.columns
    assert "Null %" in col_df.columns

    num_df = profile.to_numerical_summary_df()
    assert isinstance(num_df, pd.DataFrame)
    assert "Metric Column" in num_df.columns
    assert len(num_df) == 2  # active_minutes and quiz_score


def test_profile_all_datasets(sample_activity_df):
    """Test profiling multiple datasets simultaneously."""
    datasets = {
        "activity_1": sample_activity_df,
        "activity_2": sample_activity_df.head(3)
    }
    profiles = profile_all_datasets(datasets)

    assert "activity_1" in profiles
    assert "activity_2" in profiles
    assert profiles["activity_1"].row_count == 5
    assert profiles["activity_2"].row_count == 3


def test_generate_quality_scorecard(sample_activity_df):
    """Test generating a comparative quality scorecard across datasets."""
    datasets = {
        "students": sample_activity_df,
        "sessions": sample_activity_df
    }
    scorecard_df = generate_quality_scorecard(datasets)

    assert isinstance(scorecard_df, pd.DataFrame)
    assert len(scorecard_df) == 2
    assert "Dataset" in scorecard_df.columns
    assert "Quality Score" in scorecard_df.columns
    assert "Completeness %" in scorecard_df.columns


def test_workflow_profiling_integration(sample_activity_df):
    """Test that DataWorkflow records dataset profiles during execution."""
    workflow = DataWorkflow(name="ProfilingWorkflow")
    result = workflow.run_full_pipeline(source={"activity": sample_activity_df})

    assert result["status"] == "SUCCESS"
    assert "activity" in result["datasets_profiled"]
    assert "activity" in workflow.profiles
    assert workflow.profiles["activity"].row_count == 5

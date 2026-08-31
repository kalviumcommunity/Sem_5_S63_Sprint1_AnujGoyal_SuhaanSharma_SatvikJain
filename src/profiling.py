"""
Dataset Profiling & Quality Assessment Module for Learning Analytics.
Generates structured data quality profiles, column-level statistics, duplicate counts,
and quality scorecards suitable for Streamlit visualization and reporting.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from src.utils import setup_logger, timed_step

logger = setup_logger(__name__)


@dataclass
class DatasetProfile:
    """Represents the structured quality profile of a dataset."""
    dataset_name: str
    row_count: int
    column_count: int
    duplicate_count: int
    duplicate_percentage: float
    total_cells: int
    total_missing_cells: int
    completeness_percentage: float
    quality_score: float
    memory_usage_mb: float
    column_profiles: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    numerical_summary: Dict[str, Dict[str, float]] = field(default_factory=dict)
    categorical_summary: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Converts profile into a serializable dictionary."""
        return {
            "dataset_name": self.dataset_name,
            "row_count": self.row_count,
            "column_count": self.column_count,
            "duplicate_count": self.duplicate_count,
            "duplicate_percentage": round(self.duplicate_percentage, 2),
            "total_cells": self.total_cells,
            "total_missing_cells": self.total_missing_cells,
            "completeness_percentage": round(self.completeness_percentage, 2),
            "quality_score": round(self.quality_score, 2),
            "memory_usage_mb": round(self.memory_usage_mb, 4),
            "column_profiles": self.column_profiles,
            "numerical_summary": self.numerical_summary,
            "categorical_summary": self.categorical_summary
        }

    def to_column_summary_df(self) -> pd.DataFrame:
        """Converts column-level profiles to a DataFrame for tabular display in Streamlit."""
        records = []
        for col, meta in self.column_profiles.items():
            records.append({
                "Column": col,
                "Data Type": meta.get("dtype"),
                "Null Count": meta.get("null_count"),
                "Null %": meta.get("null_percentage"),
                "Unique Values": meta.get("unique_count"),
                "Sample Values": ", ".join(str(v) for v in meta.get("sample_values", [])[:3])
            })
        return pd.DataFrame(records)

    def to_numerical_summary_df(self) -> pd.DataFrame:
        """Converts numerical summary statistics to a DataFrame."""
        if not self.numerical_summary:
            return pd.DataFrame()
        return pd.DataFrame(self.numerical_summary).T.reset_index().rename(columns={"index": "Metric Column"})


@timed_step("Profile Dataset")
def profile_dataset(df: pd.DataFrame, dataset_name: str = "Dataset") -> DatasetProfile:
    """
    Generates a comprehensive quality profile for a given DataFrame.
    Calculates dimensional metrics, missingness, duplicates, column summaries,
    numerical statistics, and an overall quality health score (0-100).
    """
    if df is None or df.empty:
        logger.warning(f"Profiling called on empty or None DataFrame: '{dataset_name}'")
        return DatasetProfile(
            dataset_name=dataset_name,
            row_count=0,
            column_count=0,
            duplicate_count=0,
            duplicate_percentage=0.0,
            total_cells=0,
            total_missing_cells=0,
            completeness_percentage=0.0,
            quality_score=0.0,
            memory_usage_mb=0.0,
            column_profiles={},
            numerical_summary={},
            categorical_summary={}
        )

    row_count = len(df)
    col_count = len(df.columns)
    total_cells = row_count * col_count
    total_missing = int(df.isnull().sum().sum())
    completeness = ((total_cells - total_missing) / total_cells * 100.0) if total_cells > 0 else 0.0

    duplicate_count = int(df.duplicated().sum())
    duplicate_pct = (duplicate_count / row_count * 100.0) if row_count > 0 else 0.0

    memory_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)

    # Calculate overall quality score: weighted average of completeness and non-duplication
    uniqueness_rate = max(0.0, 100.0 - duplicate_pct)
    quality_score = (completeness * 0.7) + (uniqueness_rate * 0.3)

    # 1. Column-Level Profiling
    column_profiles = {}
    for col in df.columns:
        null_cnt = int(df[col].isnull().sum())
        null_pct = round((null_cnt / row_count * 100.0), 2)
        unique_cnt = int(df[col].nunique(dropna=True))
        unique_pct = round((unique_cnt / row_count * 100.0), 2)
        samples = df[col].dropna().head(3).tolist()

        column_profiles[col] = {
            "dtype": str(df[col].dtype),
            "null_count": null_cnt,
            "null_percentage": null_pct,
            "unique_count": unique_cnt,
            "unique_percentage": unique_pct,
            "sample_values": samples
        }

    # 2. Numerical Summary Statistics
    num_cols = df.select_dtypes(include=[np.number]).columns
    numerical_summary = {}
    for col in num_cols:
        series = df[col].dropna()
        if not series.empty:
            numerical_summary[col] = {
                "count": float(len(series)),
                "mean": round(float(series.mean()), 2),
                "std": round(float(series.std()), 2) if len(series) > 1 else 0.0,
                "min": round(float(series.min()), 2),
                "25%": round(float(series.quantile(0.25)), 2),
                "50% (median)": round(float(series.median()), 2),
                "75%": round(float(series.quantile(0.75)), 2),
                "max": round(float(series.max()), 2)
            }

    # 3. Categorical Summary Statistics
    cat_cols = df.select_dtypes(include=["object", "string", "category"]).columns
    categorical_summary = {}
    for col in cat_cols:
        series = df[col].dropna().astype(str)
        if not series.empty:
            top_counts = series.value_counts().head(5).to_dict()
            mode_val = series.mode().iloc[0] if not series.mode().empty else None
            categorical_summary[col] = {
                "unique_categories": int(series.nunique()),
                "mode": mode_val,
                "top_categories": top_counts
            }

    profile = DatasetProfile(
        dataset_name=dataset_name,
        row_count=row_count,
        column_count=col_count,
        duplicate_count=duplicate_count,
        duplicate_percentage=duplicate_pct,
        total_cells=total_cells,
        total_missing_cells=total_missing,
        completeness_percentage=completeness,
        quality_score=quality_score,
        memory_usage_mb=memory_mb,
        column_profiles=column_profiles,
        numerical_summary=numerical_summary,
        categorical_summary=categorical_summary
    )

    logger.info(
        f"Profiled '{dataset_name}': {row_count} rows, {col_count} cols, "
        f"Completeness={completeness:.1f}%, QualityScore={quality_score:.1f}/100"
    )
    return profile


def profile_all_datasets(datasets: Dict[str, pd.DataFrame]) -> Dict[str, DatasetProfile]:
    """Profiles a collection of named datasets."""
    profiles = {}
    for name, df in datasets.items():
        profiles[name] = profile_dataset(df, dataset_name=name)
    return profiles


def generate_quality_scorecard(datasets: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Generates a comparative quality scorecard across multiple datasets.
    Returns a DataFrame suitable for display on dashboards and reports.
    """
    records = []
    for name, df in datasets.items():
        prof = profile_dataset(df, dataset_name=name)
        records.append({
            "Dataset": name,
            "Rows": prof.row_count,
            "Columns": prof.column_count,
            "Duplicates": prof.duplicate_count,
            "Missing Values": prof.total_missing_cells,
            "Completeness %": f"{prof.completeness_percentage:.1f}%",
            "Quality Score": f"{prof.quality_score:.1f} / 100",
            "Memory (MB)": f"{prof.memory_usage_mb:.3f}"
        })
    return pd.DataFrame(records)

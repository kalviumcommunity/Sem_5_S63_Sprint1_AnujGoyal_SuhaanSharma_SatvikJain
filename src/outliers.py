"""
Statistical Outlier Detection Module for Learning Analytics.
Provides IQR, Z-score, and domain-bounded anomaly classification for educational telemetry
(session duration, quiz scores, course progress, attempt frequency) without destructive blind deletion.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple, Union
import numpy as np
import pandas as pd
from src.utils import setup_logger, timed_step

logger = setup_logger(__name__)

# Domain / Physical Constraints for Core Educational Metrics
DOMAIN_BOUNDS: Dict[str, Tuple[float, float]] = {
    "score_percentage": (0.0, 100.0),
    "quiz_score": (0.0, 100.0),
    "progress_pct": (0.0, 100.0),
    "course_progress": (0.0, 100.0),
    "duration_minutes": (0.1, 720.0),  # Max 12 hours continuous session
    "active_minutes": (0.0, 720.0),
    "idle_minutes": (0.0, 720.0),
    "age": (15.0, 90.0),
    "attempt_number": (1.0, 20.0),
    "time_taken_minutes": (0.5, 300.0)
}


@dataclass
class ColumnOutlierSummary:
    """Statistical summary of outlier detection for a single numerical column."""
    column_name: str
    method: str
    total_count: int
    mean: float
    std: float
    median: float
    q1: float
    q3: float
    iqr: float
    lower_bound: float
    upper_bound: float
    outlier_count: int
    outlier_percentage: float
    extreme_outlier_count: int
    domain_anomalies_count: int

    def to_dict(self) -> Dict[str, Any]:
        """Converts summary to dictionary."""
        return {
            "column_name": self.column_name,
            "method": self.method.upper(),
            "total_count": self.total_count,
            "mean": round(self.mean, 2),
            "std": round(self.std, 2),
            "median": round(self.median, 2),
            "q1": round(self.q1, 2),
            "q3": round(self.q3, 2),
            "iqr": round(self.iqr, 2),
            "lower_bound": round(self.lower_bound, 2),
            "upper_bound": round(self.upper_bound, 2),
            "outlier_count": self.outlier_count,
            "outlier_percentage": round(self.outlier_percentage, 2),
            "extreme_outlier_count": self.extreme_outlier_count,
            "domain_anomalies_count": self.domain_anomalies_count
        }


@dataclass
class OutlierReport:
    """Comprehensive dataset-level outlier audit report."""
    dataset_name: str
    total_records: int
    records_with_outliers: int
    outlier_percentage: float
    column_summaries: Dict[str, ColumnOutlierSummary] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Converts report to dictionary representation."""
        return {
            "dataset_name": self.dataset_name,
            "total_records": self.total_records,
            "records_with_outliers": self.records_with_outliers,
            "outlier_percentage": round(self.outlier_percentage, 2),
            "column_summaries": {k: v.to_dict() for k, v in self.column_summaries.items()}
        }

    def to_summary_df(self) -> pd.DataFrame:
        """Converts column-level outlier summaries into a DataFrame for tabular dashboards."""
        rows = [v.to_dict() for v in self.column_summaries.values()]
        return pd.DataFrame(rows) if rows else pd.DataFrame()


def calculate_iqr_bounds(
    series: pd.Series,
    multiplier: float = 1.5
) -> Tuple[float, float, float, float, float]:
    """
    Computes Q1, Q3, IQR, Lower Bound, and Upper Bound.
    """
    clean = pd.to_numeric(series, errors="coerce").dropna()
    if clean.empty:
        return 0.0, 0.0, 0.0, 0.0, 0.0

    q1 = float(clean.quantile(0.25))
    q3 = float(clean.quantile(0.75))
    iqr = q3 - q1
    lower = q1 - multiplier * iqr
    upper = q3 + multiplier * iqr
    return q1, q3, iqr, lower, upper


def calculate_zscore(
    series: pd.Series
) -> Tuple[pd.Series, float, float]:
    """
    Computes standard Z-scores for a numerical series.
    """
    clean = pd.to_numeric(series, errors="coerce")
    mean = float(clean.mean())
    std = float(clean.std())
    if np.isnan(std) or std == 0:
        return pd.Series(0.0, index=series.index), mean, 0.0
    z_scores = (clean - mean) / std
    return z_scores, mean, std


def detect_column_outliers(
    series: pd.Series,
    column_name: str = "value",
    method: str = "iqr",
    z_threshold: float = 3.0,
    domain_bounds: Optional[Tuple[float, float]] = None
) -> Tuple[pd.Series, ColumnOutlierSummary]:
    """
    Detects and classifies outliers in a single numerical series without deletion.
    
    Returns:
    - classification_series: Categorical tags ('Normal', 'Mild Outlier', 'Extreme Outlier', 'Domain Anomaly')
    - ColumnOutlierSummary dataclass
    """
    clean_s = pd.to_numeric(series, errors="coerce")
    total_cnt = len(clean_s)
    mean_val = float(clean_s.mean()) if not clean_s.empty else 0.0
    std_val = float(clean_s.std()) if not clean_s.empty else 0.0
    median_val = float(clean_s.median()) if not clean_s.empty else 0.0

    # 1. Statistical bounds
    q1, q3, iqr, lower_bound, upper_bound = calculate_iqr_bounds(clean_s, multiplier=1.5)
    _, _, _, ext_lower, ext_upper = calculate_iqr_bounds(clean_s, multiplier=3.0)

    # 2. Domain / Physical boundaries check
    bounds = domain_bounds or DOMAIN_BOUNDS.get(column_name.lower())
    dom_min, dom_max = bounds if bounds else (-np.inf, np.inf)

    # 3. Classify records
    classifications = []
    outlier_count = 0
    extreme_count = 0
    anomaly_count = 0

    z_scores, _, _ = calculate_zscore(clean_s)

    for idx, val in clean_s.items():
        if pd.isna(val):
            classifications.append("Missing")
            continue

        # Check physical anomaly
        if val < dom_min or val > dom_max:
            classifications.append("Domain Anomaly")
            anomaly_count += 1
            outlier_count += 1
            extreme_count += 1
            continue

        if method.lower() == "zscore":
            z = abs(z_scores.loc[idx])
            if z >= 3.5:
                classifications.append("Extreme Outlier")
                extreme_count += 1
                outlier_count += 1
            elif z >= z_threshold:
                classifications.append("Mild Outlier")
                outlier_count += 1
            else:
                classifications.append("Normal")
        else:
            # Default IQR method
            if val < ext_lower or val > ext_upper:
                classifications.append("Extreme Outlier")
                extreme_count += 1
                outlier_count += 1
            elif val < lower_bound or val > upper_bound:
                classifications.append("Mild Outlier")
                outlier_count += 1
            else:
                classifications.append("Normal")

    outlier_pct = (outlier_count / total_cnt * 100.0) if total_cnt > 0 else 0.0

    summary = ColumnOutlierSummary(
        column_name=column_name,
        method=method,
        total_count=total_cnt,
        mean=mean_val if not np.isnan(mean_val) else 0.0,
        std=std_val if not np.isnan(std_val) else 0.0,
        median=median_val if not np.isnan(median_val) else 0.0,
        q1=q1,
        q3=q3,
        iqr=iqr,
        lower_bound=lower_bound,
        upper_bound=upper_bound,
        outlier_count=outlier_count,
        outlier_percentage=outlier_pct,
        extreme_outlier_count=extreme_count,
        domain_anomalies_count=anomaly_count
    )

    return pd.Series(classifications, index=series.index), summary


@timed_step("Tag Dataset Outliers")
def tag_dataset_outliers(
    df: pd.DataFrame,
    entity_name: Optional[str] = None,
    target_columns: Optional[List[str]] = None,
    method: str = "iqr"
) -> Tuple[pd.DataFrame, OutlierReport]:
    """
    Enriches a DataFrame with statistical outlier flags and classification labels
    WITHOUT deleting records.
    """
    ent_name = entity_name or "Dataset"
    if df is None or df.empty:
        report = OutlierReport(
            dataset_name=ent_name,
            total_records=0,
            records_with_outliers=0,
            outlier_percentage=0.0
        )
        return pd.DataFrame() if df is None else df, report

    enriched = df.copy()
    
    # Identify candidate numerical columns
    cols_to_check = target_columns
    if not cols_to_check:
        num_cols = enriched.select_dtypes(include=[np.number]).columns.tolist()
        # Exclude binary flags and ID-like integers
        cols_to_check = [c for c in num_cols if not c.endswith("_id") and c not in ("passed", "is_weekend")]

    col_summaries = {}
    outlier_mask = pd.Series(False, index=enriched.index)

    for col in cols_to_check:
        if col in enriched.columns:
            class_series, summary = detect_column_outliers(
                enriched[col],
                column_name=col,
                method=method
            )
            enriched[f"{col}_outlier_class"] = class_series
            enriched[f"{col}_is_outlier"] = class_series.isin(["Mild Outlier", "Extreme Outlier", "Domain Anomaly"]).astype(int)
            col_summaries[col] = summary
            
            # Track any outlier
            outlier_mask = outlier_mask | (enriched[f"{col}_is_outlier"] == 1)

    records_with_outliers = int(outlier_mask.sum())
    total_records = len(enriched)
    total_outlier_pct = (records_with_outliers / total_records * 100.0) if total_records > 0 else 0.0

    report = OutlierReport(
        dataset_name=ent_name,
        total_records=total_records,
        records_with_outliers=records_with_outliers,
        outlier_percentage=total_outlier_pct,
        column_summaries=col_summaries
    )

    logger.info(
        f"Analyzed outliers for '{ent_name}': {records_with_outliers}/{total_records} rows tagged "
        f"({total_outlier_pct:.1f}% rows with statistical anomalies across {len(col_summaries)} columns)"
    )

    return enriched, report


def generate_outlier_scorecard(
    reports: Dict[str, OutlierReport]
) -> pd.DataFrame:
    """
    Consolidates multiple dataset OutlierReports into a single comparative scorecard.
    """
    rows = []
    for d_name, rep in reports.items():
        for col, s in rep.column_summaries.items():
            rows.append({
                "Dataset": d_name,
                "Variable": col,
                "Method": s.method.upper(),
                "Median": s.median,
                "IQR / Std": f"{s.iqr:.1f} (IQR)" if s.method == "iqr" else f"{s.std:.1f} (Std)",
                "Normal Range": f"[{s.lower_bound:.1f}, {s.upper_bound:.1f}]",
                "Outliers Count": s.outlier_count,
                "Outliers %": f"{s.outlier_percentage:.1f}%",
                "Extreme Outliers": s.extreme_outlier_count,
                "Domain Anomalies": s.domain_anomalies_count
            })
    return pd.DataFrame(rows)

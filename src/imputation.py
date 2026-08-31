"""
Missing Value Detection & Imputation Module for Learning Analytics.
Provides domain-aware missing value detection, column-specific imputation strategies,
unrecoverable record removal, and before/after data quality audit reports.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple, Union
import numpy as np
import pandas as pd
from src.utils import setup_logger, timed_step

logger = setup_logger(__name__)


@dataclass
class ImputationReport:
    """Represents a before-and-after audit report for missing value treatment."""
    dataset_name: str
    initial_rows: int
    final_rows: int
    dropped_rows: int
    initial_missing_cells: int
    final_missing_cells: int
    initial_completeness_pct: float
    final_completeness_pct: float
    column_actions: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Converts audit report to dictionary."""
        return {
            "dataset_name": self.dataset_name,
            "initial_rows": self.initial_rows,
            "final_rows": self.final_rows,
            "dropped_rows": self.dropped_rows,
            "initial_missing_cells": self.initial_missing_cells,
            "final_missing_cells": self.final_missing_cells,
            "initial_completeness_pct": round(self.initial_completeness_pct, 2),
            "final_completeness_pct": round(self.final_completeness_pct, 2),
            "column_actions": self.column_actions
        }

    def to_comparison_df(self) -> pd.DataFrame:
        """Converts column-level imputation actions into a DataFrame for tabular display."""
        records = []
        for col, action in self.column_actions.items():
            records.append({
                "Column": col,
                "Strategy Applied": action.get("strategy"),
                "Missing (Before)": action.get("missing_before"),
                "Missing (After)": action.get("missing_after"),
                "Imputed Value / Method": str(action.get("imputed_value")),
            })
        return pd.DataFrame(records)


def detect_missing_values(df: pd.DataFrame, dataset_name: str = "Dataset") -> Dict[str, Any]:
    """
    Detects missing values across columns and rows in a DataFrame.
    """
    if df is None or df.empty:
        return {
            "dataset_name": dataset_name,
            "total_missing_cells": 0,
            "missing_percentage": 0.0,
            "rows_with_missing": 0,
            "column_missing": {}
        }

    total_rows = len(df)
    total_cells = total_rows * len(df.columns)
    null_counts = df.isnull().sum()
    total_missing = int(null_counts.sum())
    missing_pct = (total_missing / total_cells * 100.0) if total_cells > 0 else 0.0
    rows_with_missing = int((df.isnull().any(axis=1)).sum())

    col_missing = {}
    for col in df.columns:
        cnt = int(null_counts[col])
        if cnt > 0:
            col_missing[col] = {
                "missing_count": cnt,
                "missing_percentage": round(cnt / total_rows * 100.0, 2),
                "dtype": str(df[col].dtype)
            }

    return {
        "dataset_name": dataset_name,
        "total_missing_cells": total_missing,
        "missing_percentage": round(missing_pct, 2),
        "rows_with_missing": rows_with_missing,
        "column_missing": col_missing
    }


def _impute_students(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Dict[str, Any]]]:
    """Applies domain rules for students dataset."""
    cleaned = df.copy()
    actions = {}

    # Critical key: drop if student_id is null
    initial_cnt = len(cleaned)
    cleaned = cleaned.dropna(subset=["student_id"]) if "student_id" in cleaned.columns else cleaned
    actions["student_id"] = {
        "strategy": "Drop Null Keys",
        "missing_before": initial_cnt - len(cleaned),
        "missing_after": 0,
        "imputed_value": "Dropped Invalid Rows"
    }

    # Age: Median imputation
    if "age" in cleaned.columns:
        miss_before = int(cleaned["age"].isnull().sum())
        if miss_before > 0:
            median_age = float(pd.to_numeric(cleaned["age"], errors="coerce").median())
            median_val = round(median_age) if not np.isnan(median_age) else 24
            cleaned["age"] = pd.to_numeric(cleaned["age"], errors="coerce").fillna(median_val).astype(int)
            actions["age"] = {
                "strategy": "Median Imputation",
                "missing_before": miss_before,
                "missing_after": int(cleaned["age"].isnull().sum()),
                "imputed_value": median_val
            }

    # Categorical demographics: Fill with explicit 'Unknown'
    cat_cols = ["gender", "education_level", "device_type"]
    for col in cat_cols:
        if col in cleaned.columns:
            miss_before = int(cleaned[col].isnull().sum())
            if miss_before > 0:
                cleaned[col] = cleaned[col].fillna("Unknown").replace("", "Unknown")
                actions[col] = {
                    "strategy": "Explicit Category 'Unknown'",
                    "missing_before": miss_before,
                    "missing_after": int(cleaned[col].isnull().sum()),
                    "imputed_value": "Unknown"
                }

    # Target Course ID: Fill with 'Unassigned' if missing
    if "target_course_id" in cleaned.columns:
        miss_before = int(cleaned["target_course_id"].isnull().sum())
        if miss_before > 0:
            cleaned["target_course_id"] = cleaned["target_course_id"].fillna("Unassigned")
            actions["target_course_id"] = {
                "strategy": "Default 'Unassigned'",
                "missing_before": miss_before,
                "missing_after": 0,
                "imputed_value": "Unassigned"
            }

    # Completion Status: Fill with 'In Progress'
    if "completion_status" in cleaned.columns:
        miss_before = int(cleaned["completion_status"].isnull().sum())
        if miss_before > 0:
            cleaned["completion_status"] = cleaned["completion_status"].fillna("In Progress")
            actions["completion_status"] = {
                "strategy": "Default 'In Progress'",
                "missing_before": miss_before,
                "missing_after": 0,
                "imputed_value": "In Progress"
            }

    return cleaned, actions


def _impute_courses(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Dict[str, Any]]]:
    """Applies domain rules for courses dataset."""
    cleaned = df.copy()
    actions = {}

    if "course_id" in cleaned.columns:
        cleaned = cleaned.dropna(subset=["course_id"])

    if "category" in cleaned.columns:
        miss_before = int(cleaned["category"].isnull().sum())
        if miss_before > 0:
            cleaned["category"] = cleaned["category"].fillna("General")
            actions["category"] = {
                "strategy": "Explicit Category 'General'",
                "missing_before": miss_before,
                "missing_after": 0,
                "imputed_value": "General"
            }

    for col in ["total_modules", "total_quizzes", "estimated_duration_hours"]:
        if col in cleaned.columns:
            miss_before = int(cleaned[col].isnull().sum())
            if miss_before > 0:
                med_val = float(pd.to_numeric(cleaned[col], errors="coerce").median())
                med_val = med_val if not np.isnan(med_val) else 10.0
                cleaned[col] = pd.to_numeric(cleaned[col], errors="coerce").fillna(med_val)
                actions[col] = {
                    "strategy": "Domain Median Imputation",
                    "missing_before": miss_before,
                    "missing_after": 0,
                    "imputed_value": round(med_val, 1)
                }

    return cleaned, actions


def _impute_sessions(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Dict[str, Any]]]:
    """Applies domain rules for sessions activity dataset."""
    cleaned = df.copy()
    actions = {}

    # Drop unrecoverable records missing primary/foreign keys
    key_cols = [c for c in ["session_id", "student_id", "course_id"] if c in cleaned.columns]
    if key_cols:
        initial_len = len(cleaned)
        cleaned = cleaned.dropna(subset=key_cols)
        actions["session_keys"] = {
            "strategy": "Drop Null Keys",
            "missing_before": initial_len - len(cleaned),
            "missing_after": 0,
            "imputed_value": "Dropped Invalid Rows"
        }

    # Numeric durations
    for col in ["duration_minutes", "active_minutes", "idle_minutes"]:
        if col in cleaned.columns:
            cleaned[col] = pd.to_numeric(cleaned[col], errors="coerce")

    # Logical relationship recovery
    if "duration_minutes" in cleaned.columns:
        dur_miss = int(cleaned["duration_minutes"].isnull().sum())
        if dur_miss > 0:
            if "active_minutes" in cleaned.columns and "idle_minutes" in cleaned.columns:
                cleaned["duration_minutes"] = cleaned["duration_minutes"].fillna(
                    cleaned["active_minutes"].fillna(0) + cleaned["idle_minutes"].fillna(0)
                )
            med_dur = float(cleaned["duration_minutes"].median())
            med_dur = med_dur if not np.isnan(med_dur) else 30.0
            cleaned["duration_minutes"] = cleaned["duration_minutes"].fillna(med_dur)
            actions["duration_minutes"] = {
                "strategy": "Computed / Median Duration",
                "missing_before": dur_miss,
                "missing_after": 0,
                "imputed_value": f"Sum or Median ({med_dur:.1f}m)"
            }

    if "active_minutes" in cleaned.columns:
        act_miss = int(cleaned["active_minutes"].isnull().sum())
        if act_miss > 0:
            if "duration_minutes" in cleaned.columns and "idle_minutes" in cleaned.columns:
                cleaned["active_minutes"] = cleaned["active_minutes"].fillna(
                    (cleaned["duration_minutes"] - cleaned["idle_minutes"].fillna(0)).clip(lower=0)
                )
            med_act = float(cleaned["active_minutes"].median())
            med_act = med_act if not np.isnan(med_act) else 25.0
            cleaned["active_minutes"] = cleaned["active_minutes"].fillna(med_act)
            actions["active_minutes"] = {
                "strategy": "Duration Delta / Median Active",
                "missing_before": act_miss,
                "missing_after": 0,
                "imputed_value": f"Delta or Median ({med_act:.1f}m)"
            }

    if "idle_minutes" in cleaned.columns:
        idle_miss = int(cleaned["idle_minutes"].isnull().sum())
        if idle_miss > 0:
            if "duration_minutes" in cleaned.columns and "active_minutes" in cleaned.columns:
                cleaned["idle_minutes"] = cleaned["idle_minutes"].fillna(
                    (cleaned["duration_minutes"] - cleaned["active_minutes"].fillna(0)).clip(lower=0)
                )
            cleaned["idle_minutes"] = cleaned["idle_minutes"].fillna(0.0)
            actions["idle_minutes"] = {
                "strategy": "Calculated Idle / Zero Fill",
                "missing_before": idle_miss,
                "missing_after": 0,
                "imputed_value": "Duration - Active (Min: 0)"
            }

    return cleaned, actions


def _impute_quizzes(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Dict[str, Any]]]:
    """Applies domain rules for quizzes dataset."""
    cleaned = df.copy()
    actions = {}

    key_cols = [c for c in ["quiz_attempt_id", "student_id", "quiz_id"] if c in cleaned.columns]
    if key_cols:
        initial_len = len(cleaned)
        cleaned = cleaned.dropna(subset=key_cols)
        actions["quiz_keys"] = {
            "strategy": "Drop Null Keys",
            "missing_before": initial_len - len(cleaned),
            "missing_after": 0,
            "imputed_value": "Dropped Invalid Rows"
        }

    # Attempt Number: Default to 1
    if "attempt_number" in cleaned.columns:
        miss_before = int(cleaned["attempt_number"].isnull().sum())
        if miss_before > 0:
            cleaned["attempt_number"] = pd.to_numeric(cleaned["attempt_number"], errors="coerce").fillna(1).astype(int)
            actions["attempt_number"] = {
                "strategy": "Default Attempt 1",
                "missing_before": miss_before,
                "missing_after": 0,
                "imputed_value": 1
            }

    # Score Percentage: Median assessment score (NEVER blindly 0)
    if "score_percentage" in cleaned.columns:
        miss_before = int(cleaned["score_percentage"].isnull().sum())
        if miss_before > 0:
            cleaned["score_percentage"] = pd.to_numeric(cleaned["score_percentage"], errors="coerce")
            # Calculate quiz-specific median or fallback to overall median
            overall_med = float(cleaned["score_percentage"].median())
            overall_med = overall_med if not np.isnan(overall_med) else 75.0
            
            if "quiz_id" in cleaned.columns:
                cleaned["score_percentage"] = cleaned.groupby("quiz_id")["score_percentage"].transform(
                    lambda s: s.fillna(s.median() if not np.isnan(s.median()) else overall_med)
                )
            cleaned["score_percentage"] = cleaned["score_percentage"].fillna(overall_med)
            actions["score_percentage"] = {
                "strategy": "Quiz-Specific / Global Median Imputation",
                "missing_before": miss_before,
                "missing_after": int(cleaned["score_percentage"].isnull().sum()),
                "imputed_value": f"Median Score ({overall_med:.1f}%)"
            }

    # Time Taken: Median time taken
    if "time_taken_minutes" in cleaned.columns:
        miss_before = int(cleaned["time_taken_minutes"].isnull().sum())
        if miss_before > 0:
            med_time = float(pd.to_numeric(cleaned["time_taken_minutes"], errors="coerce").median())
            med_time = med_time if not np.isnan(med_time) else 15.0
            cleaned["time_taken_minutes"] = pd.to_numeric(cleaned["time_taken_minutes"], errors="coerce").fillna(med_time)
            actions["time_taken_minutes"] = {
                "strategy": "Median Time Taken",
                "missing_before": miss_before,
                "missing_after": 0,
                "imputed_value": f"{med_time:.1f} mins"
            }

    # Passed: Compute logically from score_percentage >= 70.0
    if "score_percentage" in cleaned.columns and "passed" in cleaned.columns:
        miss_before = int(cleaned["passed"].isnull().sum())
        if miss_before > 0:
            cleaned["passed"] = (cleaned["score_percentage"] >= 70.0).astype(int)
            actions["passed"] = {
                "strategy": "Computed Logical Flag (score >= 70%)",
                "missing_before": miss_before,
                "missing_after": 0,
                "imputed_value": "1 if score>=70 else 0"
            }

    return cleaned, actions


def _impute_generic(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Dict[str, Any]]]:
    """Fallback generic imputation for unclassified tables."""
    cleaned = df.copy()
    actions = {}
    for col in cleaned.columns:
        miss_before = int(cleaned[col].isnull().sum())
        if miss_before > 0:
            if pd.api.types.is_numeric_dtype(cleaned[col]):
                med = cleaned[col].median()
                cleaned[col] = cleaned[col].fillna(med)
                actions[col] = {
                    "strategy": "Numeric Median Imputation",
                    "missing_before": miss_before,
                    "missing_after": 0,
                    "imputed_value": med
                }
            else:
                cleaned[col] = cleaned[col].fillna("Unknown")
                actions[col] = {
                    "strategy": "Categorical 'Unknown'",
                    "missing_before": miss_before,
                    "missing_after": 0,
                    "imputed_value": "Unknown"
                }
    return cleaned, actions


@timed_step("Impute Dataset Missing Values")
def impute_dataset(
    df: pd.DataFrame,
    entity_name: Optional[str] = None,
    dataset_name: str = "Dataset"
) -> Tuple[pd.DataFrame, ImputationReport]:
    """
    Applies domain-aware missing value treatment and generates a before/after audit report.
    """
    d_name = entity_name or dataset_name
    if df is None or df.empty:
        report = ImputationReport(
            dataset_name=d_name,
            initial_rows=0,
            final_rows=0,
            dropped_rows=0,
            initial_missing_cells=0,
            final_missing_cells=0,
            initial_completeness_pct=0.0,
            final_completeness_pct=0.0
        )
        return pd.DataFrame(), report

    initial_rows = len(df)
    initial_missing = int(df.isnull().sum().sum())
    total_initial_cells = initial_rows * len(df.columns)
    initial_completeness = ((total_initial_cells - initial_missing) / total_initial_cells * 100.0) if total_initial_cells > 0 else 0.0

    ent = entity_name.lower().strip() if entity_name else ""
    if ent == "students":
        imputed_df, actions = _impute_students(df)
    elif ent == "courses":
        imputed_df, actions = _impute_courses(df)
    elif ent == "sessions":
        imputed_df, actions = _impute_sessions(df)
    elif ent == "quizzes":
        imputed_df, actions = _impute_quizzes(df)
    else:
        imputed_df, actions = _impute_generic(df)

    final_rows = len(imputed_df)
    final_missing = int(imputed_df.isnull().sum().sum())
    total_final_cells = final_rows * len(imputed_df.columns) if final_rows > 0 else 1
    final_completeness = ((total_final_cells - final_missing) / total_final_cells * 100.0) if total_final_cells > 0 else 0.0

    report = ImputationReport(
        dataset_name=d_name,
        initial_rows=initial_rows,
        final_rows=final_rows,
        dropped_rows=initial_rows - final_rows,
        initial_missing_cells=initial_missing,
        final_missing_cells=final_missing,
        initial_completeness_pct=initial_completeness,
        final_completeness_pct=final_completeness,
        column_actions=actions
    )

    logger.info(
        f"Imputed '{d_name}': Missing cells {initial_missing} -> {final_missing}, "
        f"Completeness {initial_completeness:.1f}% -> {final_completeness:.1f}%, "
        f"Rows {initial_rows} -> {final_rows}"
    )

    return imputed_df, report


def impute_all_datasets(datasets: Dict[str, pd.DataFrame]) -> Tuple[Dict[str, pd.DataFrame], Dict[str, ImputationReport]]:
    """
    Imputes all project datasets across students, courses, sessions, and quizzes.
    """
    imputed_dict = {}
    reports_dict = {}

    for name, df in datasets.items():
        clean_df, rep = impute_dataset(df, entity_name=name)
        imputed_dict[name] = clean_df
        reports_dict[name] = rep

    return imputed_dict, reports_dict

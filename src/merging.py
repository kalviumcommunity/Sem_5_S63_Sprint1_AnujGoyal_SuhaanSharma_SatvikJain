"""
Multi-Source Merging & Join Validation Module for Learning Analytics.
Provides robust relational joining across students, courses, sessions, and quizzes,
with strict join validation, Cartesian explosion prevention, and transparent orphan auditing.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple, Union
import numpy as np
import pandas as pd
from src.utils import setup_logger, timed_step

logger = setup_logger(__name__)


@dataclass
class JoinValidationSummary:
    """Detailed diagnostics for a single two-table join operation."""
    left_table: str
    right_table: str
    join_type: str
    join_keys: List[str]
    left_rows: int
    right_rows: int
    joined_rows: int
    unmatched_left_rows: int
    unmatched_right_rows: int
    expansion_factor: float

    def to_dict(self) -> Dict[str, Any]:
        """Converts join summary to dictionary."""
        return {
            "Left Table": self.left_table,
            "Right Table": self.right_table,
            "Join Type": self.join_type.upper(),
            "Join Keys": ", ".join(self.join_keys),
            "Left Rows": self.left_rows,
            "Right Rows": self.right_rows,
            "Joined Rows": self.joined_rows,
            "Unmatched Left": self.unmatched_left_rows,
            "Unmatched Right": self.unmatched_right_rows,
            "Expansion Factor": f"{self.expansion_factor:.2f}x"
        }


@dataclass
class JoinAuditReport:
    """Comprehensive multi-source merge audit report and orphan diagnostics."""
    merge_name: str
    input_counts: Dict[str, int]
    output_rows: int
    output_columns: int
    join_steps: List[JoinValidationSummary] = field(default_factory=list)
    orphan_diagnostics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Converts report to dictionary representation."""
        return {
            "merge_name": self.merge_name,
            "input_counts": self.input_counts,
            "output_rows": self.output_rows,
            "output_columns": self.output_columns,
            "join_steps": [s.to_dict() for s in self.join_steps],
            "orphan_diagnostics": self.orphan_diagnostics
        }

    def to_summary_df(self) -> pd.DataFrame:
        """Converts join step diagnostics into a summary DataFrame."""
        rows = [s.to_dict() for s in self.join_steps]
        return pd.DataFrame(rows) if rows else pd.DataFrame()


def validate_two_table_join(
    left_df: pd.DataFrame,
    right_df: pd.DataFrame,
    left_on: Union[str, List[str]],
    right_on: Union[str, List[str]],
    left_name: str = "LeftTable",
    right_name: str = "RightTable",
    how: str = "left"
) -> Tuple[pd.DataFrame, JoinValidationSummary]:
    """
    Executes a merge between two DataFrames and computes integrity diagnostics.
    """
    l_keys = [left_on] if isinstance(left_on, str) else left_on
    r_keys = [right_on] if isinstance(right_on, str) else right_on

    l_len = len(left_df)
    r_len = len(right_df)

    # Perform merge with indicator to count matches
    merged = pd.merge(
        left_df,
        right_df,
        left_on=l_keys,
        right_on=r_keys,
        how=how,
        indicator="_join_indicator",
        suffixes=("", "_right")
    )

    unmatched_left = int((merged["_join_indicator"] == "left_only").sum())
    unmatched_right = 0  # In a left join, right_only records are not present in result
    
    # Calculate right table orphans that never matched
    if how == "left":
        # Check right keys present in left
        right_match = right_df.merge(
            left_df[l_keys].drop_duplicates(),
            left_on=r_keys,
            right_on=l_keys,
            how="left",
            indicator="_match_ind"
        )
        unmatched_right = int((right_match["_match_ind"] == "left_only").sum())

    merged_len = len(merged)
    expansion = (merged_len / l_len) if l_len > 0 else 1.0

    # Drop temporary join indicator
    clean_merged = merged.drop(columns=["_join_indicator"])

    summary = JoinValidationSummary(
        left_table=left_name,
        right_table=right_name,
        join_type=how,
        join_keys=l_keys,
        left_rows=l_len,
        right_rows=r_len,
        joined_rows=merged_len,
        unmatched_left_rows=unmatched_left,
        unmatched_right_rows=unmatched_right,
        expansion_factor=expansion
    )

    logger.info(
        f"Joined {left_name} ({l_len} rows) with {right_name} ({r_len} rows) -> "
        f"{merged_len} rows (Expansion: {expansion:.2f}x, Unmatched Left: {unmatched_left})"
    )

    return clean_merged, summary


def aggregate_student_sessions(sessions_df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregates session activity logs to a single row per student.
    """
    if sessions_df is None or sessions_df.empty:
        return pd.DataFrame(columns=[
            "student_id", "total_sessions", "total_duration_minutes",
            "total_active_minutes", "total_idle_minutes", "avg_session_duration",
            "active_learning_ratio", "last_session_date"
        ])

    grouped = sessions_df.groupby("student_id").agg(
        total_sessions=("session_id", "count"),
        total_duration_minutes=("duration_minutes", "sum"),
        total_active_minutes=("active_minutes", "sum"),
        total_idle_minutes=("idle_minutes", "sum"),
        avg_session_duration=("duration_minutes", "mean"),
        last_session_date=("session_start", "max")
    ).reset_index()

    grouped["total_duration_minutes"] = grouped["total_duration_minutes"].round(2)
    grouped["total_active_minutes"] = grouped["total_active_minutes"].round(2)
    grouped["total_idle_minutes"] = grouped["total_idle_minutes"].round(2)
    grouped["avg_session_duration"] = grouped["avg_session_duration"].round(2)

    # Engagement ratio: active / (duration + epsilon)
    grouped["active_learning_ratio"] = np.where(
        grouped["total_duration_minutes"] > 0,
        (grouped["total_active_minutes"] / grouped["total_duration_minutes"]).round(3),
        0.0
    )

    return grouped


def aggregate_student_quizzes(quizzes_df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregates quiz submission logs to a single row per student.
    """
    if quizzes_df is None or quizzes_df.empty:
        return pd.DataFrame(columns=[
            "student_id", "total_quiz_attempts", "quizzes_passed",
            "quizzes_failed", "avg_quiz_score", "max_quiz_score",
            "quiz_pass_rate", "latest_quiz_date"
        ])

    grouped = quizzes_df.groupby("student_id").agg(
        total_quiz_attempts=("quiz_attempt_id", "count"),
        quizzes_passed=("passed", lambda s: int((s == 1).sum())),
        quizzes_failed=("passed", lambda s: int((s == 0).sum())),
        avg_quiz_score=("score_percentage", "mean"),
        max_quiz_score=("score_percentage", "max"),
        latest_quiz_date=("attempt_date", "max")
    ).reset_index()

    grouped["avg_quiz_score"] = grouped["avg_quiz_score"].round(2)
    grouped["max_quiz_score"] = grouped["max_quiz_score"].round(2)
    grouped["quiz_pass_rate"] = np.where(
        grouped["total_quiz_attempts"] > 0,
        (grouped["quizzes_passed"] / grouped["total_quiz_attempts"] * 100.0).round(2),
        0.0
    )

    return grouped


@timed_step("Build Student 360 Dataset")
def build_student_360_dataset(
    students_df: pd.DataFrame,
    courses_df: pd.DataFrame,
    sessions_df: pd.DataFrame,
    quizzes_df: pd.DataFrame
) -> Tuple[pd.DataFrame, JoinAuditReport]:
    """
    Merges all 4 project entities into an analytical Student 360 dataset
    with strict join validation and orphan diagnostics.
    """
    input_counts = {
        "students": len(students_df) if students_df is not None else 0,
        "courses": len(courses_df) if courses_df is not None else 0,
        "sessions": len(sessions_df) if sessions_df is not None else 0,
        "quizzes": len(quizzes_df) if quizzes_df is not None else 0
    }

    join_steps: List[JoinValidationSummary] = []

    # 1. Join Students + Courses on target_course_id == course_id
    step1_df, summary1 = validate_two_table_join(
        left_df=students_df,
        right_df=courses_df,
        left_on="target_course_id",
        right_on="course_id",
        left_name="Students",
        right_name="Courses",
        how="left"
    )
    join_steps.append(summary1)

    # 2. Pre-aggregate Sessions & Left Join
    agg_sessions = aggregate_student_sessions(sessions_df)
    step2_df, summary2 = validate_two_table_join(
        left_df=step1_df,
        right_df=agg_sessions,
        left_on="student_id",
        right_on="student_id",
        left_name="StudentsWithCourses",
        right_name="AggregatedSessions",
        how="left"
    )
    join_steps.append(summary2)

    # Fill default session metrics for inactive students
    session_metric_defaults = {
        "total_sessions": 0,
        "total_duration_minutes": 0.0,
        "total_active_minutes": 0.0,
        "total_idle_minutes": 0.0,
        "avg_session_duration": 0.0,
        "active_learning_ratio": 0.0
    }
    for col, default_val in session_metric_defaults.items():
        if col in step2_df.columns:
            step2_df[col] = step2_df[col].fillna(default_val)

    # 3. Pre-aggregate Quizzes & Left Join
    agg_quizzes = aggregate_student_quizzes(quizzes_df)
    student_360_df, summary3 = validate_two_table_join(
        left_df=step2_df,
        right_df=agg_quizzes,
        left_on="student_id",
        right_on="student_id",
        left_name="StudentsWithSessions",
        right_name="AggregatedQuizzes",
        how="left"
    )
    join_steps.append(summary3)

    # Fill default quiz metrics for unassessed students
    quiz_metric_defaults = {
        "total_quiz_attempts": 0,
        "quizzes_passed": 0,
        "quizzes_failed": 0,
        "avg_quiz_score": 0.0,
        "max_quiz_score": 0.0,
        "quiz_pass_rate": 0.0
    }
    for col, default_val in quiz_metric_defaults.items():
        if col in student_360_df.columns:
            student_360_df[col] = student_360_df[col].fillna(default_val)

    # 4. Compute Derived Progress Percentage
    if "total_quizzes" in student_360_df.columns and "quizzes_passed" in student_360_df.columns:
        tot_q = student_360_df["total_quizzes"].replace(0, np.nan)
        student_360_df["progress_pct"] = (
            (student_360_df["quizzes_passed"] / tot_q * 100.0).clip(0.0, 100.0).round(2).fillna(0.0)
        )

    # 5. Diagnostic Orphan Audits
    stu_ids = set(students_df["student_id"].dropna().unique()) if "student_id" in students_df.columns else set()
    ses_stu_ids = set(sessions_df["student_id"].dropna().unique()) if "student_id" in sessions_df.columns else set()
    quiz_stu_ids = set(quizzes_df["student_id"].dropna().unique()) if "student_id" in quizzes_df.columns else set()

    orphan_sessions = len(ses_stu_ids - stu_ids)
    orphan_quizzes = len(quiz_stu_ids - stu_ids)
    inactive_students = len(stu_ids - ses_stu_ids)
    untested_students = len(stu_ids - quiz_stu_ids)

    orphan_diagnostics = {
        "orphan_sessions_unregistered_students": orphan_sessions,
        "orphan_quizzes_unregistered_students": orphan_quizzes,
        "registered_students_zero_sessions": inactive_students,
        "registered_students_zero_quizzes": untested_students,
        "granularity_preserved": len(student_360_df) == len(students_df)
    }

    report = JoinAuditReport(
        merge_name="Student360MasterDataset",
        input_counts=input_counts,
        output_rows=len(student_360_df),
        output_columns=len(student_360_df.columns),
        join_steps=join_steps,
        orphan_diagnostics=orphan_diagnostics
    )

    logger.info(
        f"Completed Student 360 Merge: {len(student_360_df)} records, "
        f"{len(student_360_df.columns)} columns across 4 entities. "
        f"Granularity preserved: {orphan_diagnostics['granularity_preserved']}"
    )

    return student_360_df, report

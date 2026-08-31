"""
Duplicate Detection & Record Deduplication Module for Learning Analytics.
Provides business-key deduplication strategies, exact vs. partial duplicate detection,
intelligent tie-breaking, and before/after cleaning audit scorecards.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple, Union
import pandas as pd
from src.utils import setup_logger, timed_step

logger = setup_logger(__name__)

# Primary and Natural Business Keys per Entity
ENTITY_BUSINESS_KEYS: Dict[str, List[str]] = {
    "students": ["student_id"],
    "courses": ["course_id"],
    "sessions": ["session_id"],
    "quizzes": ["quiz_attempt_id"]
}

ENTITY_COMPOSITE_KEYS: Dict[str, List[str]] = {
    "students": ["student_id", "target_course_id"],
    "courses": ["course_id"],
    "sessions": ["student_id", "course_id", "session_start"],
    "quizzes": ["student_id", "course_id", "quiz_id", "attempt_number"]
}


@dataclass
class DeduplicationReport:
    """Represents a structured audit report of duplicate detection and removal."""
    entity_name: str
    initial_rows: int
    final_rows: int
    exact_duplicates_removed: int
    business_key_duplicates_removed: int
    total_duplicates_removed: int
    business_keys_used: List[str] = field(default_factory=list)
    initial_duplicate_pct: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Converts report to dictionary representation."""
        return {
            "entity_name": self.entity_name,
            "initial_rows": self.initial_rows,
            "final_rows": self.final_rows,
            "exact_duplicates_removed": self.exact_duplicates_removed,
            "business_key_duplicates_removed": self.business_key_duplicates_removed,
            "total_duplicates_removed": self.total_duplicates_removed,
            "initial_duplicate_pct": round(self.initial_duplicate_pct, 2),
            "business_keys_used": self.business_keys_used
        }

    def to_summary_df(self) -> pd.DataFrame:
        """Converts audit metrics into a 1-row DataFrame for tabular dashboards."""
        return pd.DataFrame([{
            "Entity Name": self.entity_name,
            "Initial Rows": self.initial_rows,
            "Final Rows": self.final_rows,
            "Exact Duplicates Removed": self.exact_duplicates_removed,
            "Business Key Duplicates Removed": self.business_key_duplicates_removed,
            "Total Duplicates Removed": self.total_duplicates_removed,
            "Duplicate %": f"{self.initial_duplicate_pct:.1f}%",
            "Business Keys Used": ", ".join(self.business_keys_used) if self.business_keys_used else "None"
        }])


def detect_duplicates(
    df: pd.DataFrame,
    entity_name: Optional[str] = None,
    subset_keys: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Analyzes exact duplicate rows and business-key duplicate clusters in a DataFrame.
    """
    if df is None or df.empty:
        return {
            "entity_name": entity_name or "Unknown",
            "total_rows": 0,
            "exact_duplicate_rows": 0,
            "exact_duplicate_pct": 0.0,
            "business_key_duplicates": 0,
            "business_keys_used": []
        }

    total_rows = len(df)
    exact_dupes = int(df.duplicated().sum())
    exact_pct = (exact_dupes / total_rows * 100.0) if total_rows > 0 else 0.0

    # Determine business keys
    keys = subset_keys
    ent = entity_name.lower().strip() if entity_name else ""
    if not keys and ent in ENTITY_BUSINESS_KEYS:
        candidate_keys = ENTITY_BUSINESS_KEYS[ent]
        keys = [k for k in candidate_keys if k in df.columns]

    b_key_dupes = 0
    if keys:
        b_key_dupes = int(df.duplicated(subset=keys).sum())

    return {
        "entity_name": entity_name or "Dataset",
        "total_rows": total_rows,
        "exact_duplicate_rows": exact_dupes,
        "exact_duplicate_pct": round(exact_pct, 2),
        "business_key_duplicates": b_key_dupes,
        "business_keys_used": keys or []
    }


def _deduplicate_students(df: pd.DataFrame) -> Tuple[pd.DataFrame, int, List[str]]:
    """Deduplicates students by student_id, keeping the most complete record."""
    keys = [k for k in ["student_id"] if k in df.columns]
    if not keys:
        return df, 0, []

    # Sort by completeness score (non-null counts) descending
    completeness = df.notnull().sum(axis=1)
    df_sorted = df.assign(_completeness=completeness).sort_values(by="_completeness", ascending=False)
    deduped = df_sorted.drop_duplicates(subset=keys, keep="first").drop(columns=["_completeness"])
    
    removed = len(df) - len(deduped)
    return deduped, removed, keys


def _deduplicate_courses(df: pd.DataFrame) -> Tuple[pd.DataFrame, int, List[str]]:
    """Deduplicates courses by course_id."""
    keys = [k for k in ["course_id"] if k in df.columns]
    if not keys:
        return df, 0, []

    # Sort by total_modules or completeness
    sort_cols = [c for c in ["total_modules"] if c in df.columns]
    if sort_cols:
        df_sorted = df.sort_values(by=sort_cols, ascending=False)
    else:
        df_sorted = df
    deduped = df_sorted.drop_duplicates(subset=keys, keep="first")
    removed = len(df) - len(deduped)
    return deduped, removed, keys


def _deduplicate_sessions(df: pd.DataFrame) -> Tuple[pd.DataFrame, int, List[str]]:
    """Deduplicates sessions by session_id and natural composite key."""
    keys = [k for k in ["session_id"] if k in df.columns]
    if not keys:
        composite = [c for c in ["student_id", "course_id", "session_start"] if c in df.columns]
        keys = composite if len(composite) >= 2 else []

    if not keys:
        return df, 0, []

    # Sort by duration / active minutes descending so highest engagement session is preserved
    sort_cols = [c for c in ["duration_minutes", "active_minutes"] if c in df.columns]
    if sort_cols:
        df_sorted = df.sort_values(by=sort_cols, ascending=False)
    else:
        df_sorted = df
    deduped = df_sorted.drop_duplicates(subset=keys, keep="first")
    removed = len(df) - len(deduped)
    return deduped, removed, keys


def _deduplicate_quizzes(df: pd.DataFrame) -> Tuple[pd.DataFrame, int, List[str]]:
    """Deduplicates quizzes by quiz_attempt_id or (student, quiz, attempt_number)."""
    keys = [k for k in ["quiz_attempt_id"] if k in df.columns]
    if not keys:
        composite = [c for c in ["student_id", "quiz_id", "attempt_number"] if c in df.columns]
        keys = composite if len(composite) >= 2 else []

    if not keys:
        return df, 0, []

    # Sort by score_percentage descending to preserve best/validated score
    sort_cols = [c for c in ["score_percentage", "passed"] if c in df.columns]
    if sort_cols:
        df_sorted = df.sort_values(by=sort_cols, ascending=False)
    else:
        df_sorted = df
    deduped = df_sorted.drop_duplicates(subset=keys, keep="first")
    removed = len(df) - len(deduped)
    return deduped, removed, keys


@timed_step("Deduplicate Dataset Records")
def deduplicate_dataset(
    df: pd.DataFrame,
    entity_name: Optional[str] = None,
    custom_keys: Optional[List[str]] = None
) -> Tuple[pd.DataFrame, DeduplicationReport]:
    """
    Performs multi-stage deduplication:
    1. Exact full-row duplicate elimination.
    2. Business-key intelligent deduplication with domain tie-breaking.
    """
    ent_name = entity_name or "Dataset"
    if df is None or df.empty:
        report = DeduplicationReport(
            entity_name=ent_name,
            initial_rows=0,
            final_rows=0,
            exact_duplicates_removed=0,
            business_key_duplicates_removed=0,
            total_duplicates_removed=0
        )
        return pd.DataFrame() if df is None else df, report

    initial_rows = len(df)

    # Stage 1: Exact row deduplication
    stage1_df = df.drop_duplicates()
    exact_removed = initial_rows - len(stage1_df)

    # Stage 2: Business key deduplication
    ent = entity_name.lower().strip() if entity_name else ""
    if custom_keys:
        stage2_df = stage1_df.drop_duplicates(subset=custom_keys, keep="first")
        b_removed = len(stage1_df) - len(stage2_df)
        used_keys = custom_keys
    elif ent == "students":
        stage2_df, b_removed, used_keys = _deduplicate_students(stage1_df)
    elif ent == "courses":
        stage2_df, b_removed, used_keys = _deduplicate_courses(stage1_df)
    elif ent == "sessions":
        stage2_df, b_removed, used_keys = _deduplicate_sessions(stage1_df)
    elif ent == "quizzes":
        stage2_df, b_removed, used_keys = _deduplicate_quizzes(stage1_df)
    else:
        stage2_df = stage1_df
        b_removed = 0
        used_keys = []

    final_rows = len(stage2_df)
    total_removed = initial_rows - final_rows
    initial_dupe_pct = (total_removed / initial_rows * 100.0) if initial_rows > 0 else 0.0

    report = DeduplicationReport(
        entity_name=ent_name,
        initial_rows=initial_rows,
        final_rows=final_rows,
        exact_duplicates_removed=exact_removed,
        business_key_duplicates_removed=b_removed,
        total_duplicates_removed=total_removed,
        business_keys_used=used_keys,
        initial_duplicate_pct=initial_dupe_pct
    )

    logger.info(
        f"Deduplicated '{ent_name}': {initial_rows} -> {final_rows} rows "
        f"({exact_removed} exact + {b_removed} business key duplicates removed, keys: {used_keys})"
    )

    return stage2_df, report


def deduplicate_all_datasets(
    datasets: Dict[str, pd.DataFrame]
) -> Tuple[Dict[str, pd.DataFrame], Dict[str, DeduplicationReport]]:
    """
    Applies intelligent deduplication across all project entities.
    """
    deduped_dict = {}
    reports_dict = {}

    for name, df in datasets.items():
        clean_df, report = deduplicate_dataset(df, entity_name=name)
        deduped_dict[name] = clean_df
        reports_dict[name] = report

    return deduped_dict, reports_dict


def generate_deduplication_scorecard(
    reports: Dict[str, DeduplicationReport]
) -> pd.DataFrame:
    """
    Consolidates multiple DeduplicationReports into a single comparative DataFrame.
    """
    rows = []
    for name, rep in reports.items():
        rows.append({
            "Entity": name,
            "Initial Rows": rep.initial_rows,
            "Final Rows": rep.final_rows,
            "Exact Duplicates": rep.exact_duplicates_removed,
            "Business Key Duplicates": rep.business_key_duplicates_removed,
            "Total Duplicates Removed": rep.total_duplicates_removed,
            "Duplicate %": f"{rep.initial_duplicate_pct:.1f}%",
            "Business Key(s) Used": ", ".join(rep.business_keys_used) if rep.business_keys_used else "None"
        })
    return pd.DataFrame(rows)

"""
Feature Engineering & Derived Business Columns Module for Learning Analytics.
Computes mathematically grounded behavioral metrics (learning frequency, velocity, recency,
consistency, and composite engagement indices) to predict course completion and dropout risk.
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Tuple, Union
import numpy as np
import pandas as pd
from src.utils import setup_logger, timed_step

logger = setup_logger(__name__)


# Feature Definitions and Business Formulas
FEATURE_FORMULAS: Dict[str, str] = {
    "average_session_duration": "total_duration_minutes / max(total_sessions, 1) [Minutes/session]",
    "sessions_per_week": "total_sessions / max(tenure_weeks, 1.0) [Weekly study frequency]",
    "quiz_average": "Mean of score_percentage across all quiz attempts [0.0 - 100.0%]",
    "quiz_attempt_count": "Total count of quiz submissions/attempts [Integer]",
    "course_progress": "min(100.0, (quizzes_passed / total_quizzes) * 100.0) [0.0 - 100.0%]",
    "progress_velocity": "course_progress / max(tenure_weeks, 1.0) [% completion gained per week]",
    "days_since_last_activity": "max(0, (as_of_date - max(last_session, latest_quiz)).days) [Inactivity recency]",
    "completion_rate": "1.0 if completion_status == 'Completed' else 0.0 [Target Binary Indicator]",
    "learning_consistency": "0.6 * min(1.0, total_sessions / (tenure_weeks * 2.0)) + 0.4 * active_learning_ratio [0.0 - 1.0]",
    "engagement_score": "0.30 * course_progress + 0.25 * quiz_pass_rate + 0.25 * min(100, sessions_per_week * 25) + 0.20 * (active_learning_ratio * 100) [0.0 - 100.0 Index]"
}


@timed_step("Engineer Behavioral Features")
def engineer_behavioral_features(
    student_360_df: pd.DataFrame,
    as_of_date: Optional[Union[str, pd.Timestamp]] = None
) -> pd.DataFrame:
    """
    Computes all 10 core behavioral features for EdTech dropout and completion prediction.
    
    Parameters:
    - student_360_df: Enriched Student 360 DataFrame from multi-source merge.
    - as_of_date: Benchmark snapshot date for recency calculations (defaults to max activity date or today).
    
    Returns:
    - Transformed DataFrame enriched with derived analytical features.
    """
    if student_360_df is None or student_360_df.empty:
        return pd.DataFrame() if student_360_df is None else student_360_df

    df = student_360_df.copy()

    # 1. Determine As-Of Benchmark Date
    if as_of_date is not None:
        benchmark_date = pd.to_datetime(as_of_date)
    else:
        # Auto-discover latest activity timestamp across registration, sessions, and quizzes
        all_dates = []
        for col in ["registration_date", "last_session_date", "latest_quiz_date"]:
            if col in df.columns:
                dt_s = pd.to_datetime(df[col], errors="coerce").dropna()
                if not dt_s.empty:
                    all_dates.append(dt_s.max())
        benchmark_date = max(all_dates) if all_dates else pd.Timestamp.now()

    logger.info(f"Engineering behavioral features with snapshot benchmark date: {benchmark_date.strftime('%Y-%m-%d')}")

    # 2. Learner Enrolled Tenure in Weeks
    reg_dates = pd.to_datetime(df.get("registration_date", pd.Series(benchmark_date, index=df.index)), errors="coerce")
    tenure_days = (benchmark_date - reg_dates).dt.days.clip(lower=1)
    df["tenure_weeks"] = (tenure_days / 7.0).clip(lower=1.0).round(2)

    # 3. Average Session Duration
    tot_dur = pd.to_numeric(df.get("total_duration_minutes", 0.0), errors="coerce").fillna(0.0)
    tot_ses = pd.to_numeric(df.get("total_sessions", 0), errors="coerce").fillna(0)
    df["average_session_duration"] = np.where(
        tot_ses > 0,
        (tot_dur / tot_ses).round(2),
        0.0
    )

    # 4. Sessions Per Week
    df["sessions_per_week"] = (tot_ses / df["tenure_weeks"]).round(2)

    # 5. Quiz Average & Attempt Count
    df["quiz_average"] = pd.to_numeric(df.get("avg_quiz_score", 0.0), errors="coerce").fillna(0.0).round(2)
    df["quiz_attempt_count"] = pd.to_numeric(df.get("total_quiz_attempts", 0), errors="coerce").fillna(0).astype(int)

    # 6. Course Progress (%)
    tot_q = pd.to_numeric(df.get("total_quizzes", 1), errors="coerce").replace(0, np.nan).fillna(1)
    q_passed = pd.to_numeric(df.get("quizzes_passed", 0), errors="coerce").fillna(0)
    
    if "progress_pct" in df.columns:
        # Re-verify and clamp progress
        df["course_progress"] = pd.to_numeric(df["progress_pct"], errors="coerce").fillna(0.0).clip(0.0, 100.0).round(2)
    else:
        df["course_progress"] = ((q_passed / tot_q) * 100.0).clip(0.0, 100.0).round(2)

    # 7. Progress Velocity (% per week)
    df["progress_velocity"] = (df["course_progress"] / df["tenure_weeks"]).round(2)

    # 8. Days Since Last Activity (Inactivity Recency)
    last_ses_dt = pd.to_datetime(df.get("last_session_date", pd.Series(pd.NaT, index=df.index)), errors="coerce")
    last_q_dt = pd.to_datetime(df.get("latest_quiz_date", pd.Series(pd.NaT, index=df.index)), errors="coerce")
    
    # Take max valid date between session and quiz, fallback to registration
    most_recent_activity = pd.concat([last_ses_dt, last_q_dt, reg_dates], axis=1).max(axis=1)
    days_inactive = (benchmark_date - most_recent_activity).dt.days.fillna(0).clip(lower=0)
    df["days_since_last_activity"] = days_inactive.astype(int)

    # 9. Completion Rate (Binary Target Indicator)
    status_series = df.get("completion_status", pd.Series("", index=df.index)).astype(str).str.strip().str.lower()
    df["completion_rate"] = np.where(status_series == "completed", 1.0, 0.0)

    # 10. Learning Consistency Index [0.0 - 1.0]
    act_ratio = pd.to_numeric(df.get("active_learning_ratio", 0.0), errors="coerce").fillna(0.0).clip(0.0, 1.0)
    target_sessions = (df["tenure_weeks"] * 2.0).clip(lower=1.0)
    session_cadence = (tot_ses / target_sessions).clip(0.0, 1.0)
    df["learning_consistency"] = (0.6 * session_cadence + 0.4 * act_ratio).round(3)

    # 11. Composite Engagement Score [0.0 - 100.0]
    quiz_p_rate = pd.to_numeric(df.get("quiz_pass_rate", 0.0), errors="coerce").fillna(0.0).clip(0.0, 100.0)
    freq_component = (df["sessions_per_week"] * 25.0).clip(0.0, 100.0)
    
    engagement = (
        0.30 * df["course_progress"] +
        0.25 * quiz_p_rate +
        0.25 * freq_component +
        0.20 * (act_ratio * 100.0)
    )
    df["engagement_score"] = engagement.clip(0.0, 100.0).round(2)

    logger.info(
        f"Successfully engineered {len(FEATURE_FORMULAS)} behavioral features across {len(df)} learners "
        f"(Mean Engagement: {df['engagement_score'].mean():.1f}/100, Mean Velocity: {df['progress_velocity'].mean():.1f}%/wk)"
    )

    return df


def get_feature_dictionary() -> pd.DataFrame:
    """
    Returns a DataFrame documentation of all engineered behavioral features and their formulas.
    """
    rows = [{"Feature Name": k, "Mathematical Formula": v} for k, v in FEATURE_FORMULAS.items()]
    return pd.DataFrame(rows)

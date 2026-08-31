"""
NumPy Vectorised Computation Workflow Module for Learning Analytics.
Provides high-throughput SIMD vector math for feature transformations, min-max scaling,
Z-score standardization, composite engagement scoring, and multi-factor dropout risk modeling.
"""

import time
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Tuple, Union
import numpy as np
import pandas as pd
from src.utils import setup_logger, timed_step

logger = setup_logger(__name__)


def vectorized_min_max_scale(
    arr: Union[np.ndarray, pd.Series, List[float]],
    feature_range: Tuple[float, float] = (0.0, 1.0),
    eps: float = 1e-8
) -> np.ndarray:
    """
    Performs fast NumPy vectorized Min-Max scaling.
    """
    x = np.asarray(arr, dtype=np.float64)
    x_min = np.nanmin(x)
    x_max = np.nanmax(x)
    
    range_diff = x_max - x_min
    if range_diff < eps:
        return np.full_like(x, feature_range[0])
    
    scaled_std = (x - x_min) / range_diff
    scaled = scaled_std * (feature_range[1] - feature_range[0]) + feature_range[0]
    return np.clip(scaled, feature_range[0], feature_range[1])


def vectorized_zscore_standardize(
    arr: Union[np.ndarray, pd.Series, List[float]],
    eps: float = 1e-8
) -> np.ndarray:
    """
    Performs fast NumPy vectorized Z-score standardization (zero mean, unit variance).
    """
    x = np.asarray(arr, dtype=np.float64)
    mean = np.nanmean(x)
    std = np.nanstd(x)
    
    if std < eps:
        return np.zeros_like(x)
    
    return (x - mean) / std


def compute_vectorized_engagement(
    progress: np.ndarray,
    quiz_pass_rate: np.ndarray,
    sessions_per_week: np.ndarray,
    active_learning_ratio: np.ndarray
) -> np.ndarray:
    """
    Computes composite student engagement score [0.0 - 100.0] using vectorized array operations.
    Formula: 0.30*prog + 0.25*quiz_rate + 0.25*min(100, freq*25) + 0.20*(active*100)
    """
    prog_arr = np.clip(np.asarray(progress, dtype=np.float64), 0.0, 100.0)
    quiz_arr = np.clip(np.asarray(quiz_pass_rate, dtype=np.float64), 0.0, 100.0)
    freq_arr = np.clip(np.asarray(sessions_per_week, dtype=np.float64) * 25.0, 0.0, 100.0)
    act_arr = np.clip(np.asarray(active_learning_ratio, dtype=np.float64) * 100.0, 0.0, 100.0)

    # Linear combination using SIMD vector arithmetic
    engagement = (
        0.30 * prog_arr +
        0.25 * quiz_arr +
        0.25 * freq_arr +
        0.20 * act_arr
    )
    return np.clip(engagement, 0.0, 100.0)


def compute_vectorized_dropout_risk(
    engagement_scores: np.ndarray,
    days_inactive: np.ndarray,
    quiz_pass_rate: np.ndarray
) -> np.ndarray:
    """
    Computes multidimensional dropout risk score [0.0 - 100.0] using vectorized operations.
    
    Formulation:
    - Base risk = 100.0 - engagement_score
    - Inactivity penalty = min(40.0, days_inactive * 1.5)
    - Low quiz pass penalty = where(quiz_pass_rate < 50, (50 - quiz_pass_rate) * 0.4, 0.0)
    """
    eng_arr = np.clip(np.asarray(engagement_scores, dtype=np.float64), 0.0, 100.0)
    inact_arr = np.maximum(np.asarray(days_inactive, dtype=np.float64), 0.0)
    quiz_arr = np.clip(np.asarray(quiz_pass_rate, dtype=np.float64), 0.0, 100.0)

    base_risk = 100.0 - eng_arr
    inactivity_penalty = np.minimum(40.0, inact_arr * 1.5)
    quiz_penalty = np.where(quiz_arr < 50.0, (50.0 - quiz_arr) * 0.4, 0.0)

    total_risk = 0.50 * base_risk + 0.35 * inactivity_penalty + 0.15 * quiz_penalty
    return np.clip(total_risk, 0.0, 100.0)


def classify_risk_tier(risk_scores: np.ndarray) -> np.ndarray:
    """
    Vectorized categorization of dropout risk scores into actionable operational tiers:
    - Low Risk: [0.0 - 25.0)
    - Moderate Risk: [25.0 - 50.0)
    - High Risk: [50.0 - 75.0)
    - Critical Risk: [75.0 - 100.0]
    """
    scores = np.asarray(risk_scores, dtype=np.float64)
    conditions = [
        scores < 25.0,
        (scores >= 25.0) & (scores < 50.0),
        (scores >= 50.0) & (scores < 75.0),
        scores >= 75.0
    ]
    choices = ["Low", "Moderate", "High", "Critical"]
    return np.select(conditions, choices, default="Unknown")


@timed_step("Apply Vectorized Transformations")
def apply_vectorized_transformations(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enriches analytical dataset with vectorized risk, normalization, and tier classifications.
    """
    if df is None or df.empty:
        return pd.DataFrame() if df is None else df

    enriched = df.copy()

    # 1. Compute Vectorized Dropout Risk Score
    eng_s = enriched.get("engagement_score", pd.Series(50.0, index=enriched.index)).to_numpy()
    inact_s = enriched.get("days_since_last_activity", pd.Series(0, index=enriched.index)).to_numpy()
    quiz_p_s = enriched.get("quiz_pass_rate", pd.Series(50.0, index=enriched.index)).to_numpy()

    risk_scores = compute_vectorized_dropout_risk(eng_s, inact_s, quiz_p_s).round(2)
    enriched["dropout_risk_score"] = risk_scores
    enriched["risk_tier"] = classify_risk_tier(risk_scores)

    # 2. Normalized Engagement Metric [0.0 - 1.0]
    enriched["normalized_engagement"] = vectorized_min_max_scale(eng_s).round(4)
    enriched["standardized_progress"] = vectorized_zscore_standardize(
        enriched.get("course_progress", pd.Series(0.0, index=enriched.index)).to_numpy()
    ).round(4)

    logger.info(
        f"Vectorized computations applied to {len(enriched)} records: "
        f"Mean Risk: {risk_scores.mean():.1f}/100, High/Critical Risk Learners: {int((risk_scores >= 50.0).sum())}"
    )

    return enriched


def benchmark_vectorized_vs_iterative(n_records: int = 10000) -> Dict[str, Any]:
    """
    Benchmarks NumPy vectorized execution speed vs Python row-by-row iteration
    demonstrating efficiency gains on identical math operations.
    """
    np.random.seed(42)
    progress = np.random.uniform(0.0, 100.0, n_records)
    quiz_rate = np.random.uniform(0.0, 100.0, n_records)
    sessions_pw = np.random.uniform(0.0, 10.0, n_records)
    active_ratio = np.random.uniform(0.0, 1.0, n_records)
    days_inact = np.random.randint(0, 90, n_records)

    # 1. Iterative Python loop benchmark
    t0 = time.perf_counter()
    iterative_results = []
    for i in range(n_records):
        p = min(max(progress[i], 0.0), 100.0)
        q = min(max(quiz_rate[i], 0.0), 100.0)
        f = min(max(sessions_pw[i] * 25.0, 0.0), 100.0)
        a = min(max(active_ratio[i] * 100.0, 0.0), 100.0)
        eng = 0.30 * p + 0.25 * q + 0.25 * f + 0.20 * a
        
        base_risk = 100.0 - eng
        inact_pen = min(40.0, days_inact[i] * 1.5)
        quiz_pen = (50.0 - q) * 0.4 if q < 50.0 else 0.0
        risk = min(max(0.50 * base_risk + 0.35 * inact_pen + 0.15 * quiz_pen, 0.0), 100.0)
        iterative_results.append((eng, risk))
    t_iterative = time.perf_counter() - t0

    # 2. NumPy Vectorized benchmark
    t1 = time.perf_counter()
    vec_eng = compute_vectorized_engagement(progress, quiz_rate, sessions_pw, active_ratio)
    vec_risk = compute_vectorized_dropout_risk(vec_eng, days_inact, quiz_rate)
    t_vectorized = time.perf_counter() - t1

    speedup = t_iterative / max(t_vectorized, 1e-9)

    return {
        "n_records": n_records,
        "iterative_time_sec": round(t_iterative, 5),
        "vectorized_time_sec": round(t_vectorized, 5),
        "speedup_factor": round(speedup, 1),
        "numerical_parity": bool(np.allclose([r[0] for r in iterative_results], vec_eng, atol=1e-5))
    }

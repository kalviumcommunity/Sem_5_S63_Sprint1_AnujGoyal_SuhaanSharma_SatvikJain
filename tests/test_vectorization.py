"""
Unit tests for Concept #17: NumPy Vectorised Computation Workflow.
Tests Min-Max scaling, Z-score standardization, vectorized engagement,
dropout risk scoring, operational tier classification, and benchmark validation.
"""

import pytest
import numpy as np
import pandas as pd

from src.vectorization import (
    vectorized_min_max_scale,
    vectorized_zscore_standardize,
    compute_vectorized_engagement,
    compute_vectorized_dropout_risk,
    classify_risk_tier,
    apply_vectorized_transformations,
    benchmark_vectorized_vs_iterative
)


def test_vectorized_min_max_scale():
    """Test Min-Max scaling of arrays."""
    data = np.array([10.0, 20.0, 30.0, 40.0, 50.0])
    scaled = vectorized_min_max_scale(data, feature_range=(0.0, 1.0))

    assert scaled.min() == 0.0
    assert scaled.max() == 1.0
    assert scaled[2] == 0.5


def test_vectorized_zscore_standardize():
    """Test Z-score standardization."""
    data = np.array([10.0, 20.0, 30.0, 40.0, 50.0])
    z = vectorized_zscore_standardize(data)

    assert pytest.approx(z.mean(), abs=1e-6) == 0.0
    assert pytest.approx(z.std(), abs=1e-6) == 1.0


def test_compute_vectorized_engagement():
    """Test vectorized engagement composite index calculation."""
    prog = np.array([100.0, 0.0])
    quiz = np.array([100.0, 0.0])
    freq = np.array([4.0, 0.0])      # 4 * 25 = 100
    act = np.array([1.0, 0.0])       # 1.0 * 100 = 100

    eng = compute_vectorized_engagement(prog, quiz, freq, act)

    assert eng[0] == 100.0  # Perfect active student
    assert eng[1] == 0.0    # Inactive cold-start student


def test_compute_vectorized_dropout_risk_and_tiers():
    """Test multi-factor dropout risk computation and tier classification."""
    eng = np.array([90.0, 20.0, 5.0])
    days_inact = np.array([1, 15, 60])
    quiz_p = np.array([95.0, 40.0, 10.0])

    risk = compute_vectorized_dropout_risk(eng, days_inact, quiz_p)
    tiers = classify_risk_tier(risk)

    assert risk[0] < risk[1] < risk[2]
    assert tiers[0] == "Low"
    assert tiers[2] in ("High", "Critical")


def test_apply_vectorized_transformations():
    """Test DataFrame enrichment with vectorized outputs."""
    df = pd.DataFrame({
        "student_id": ["S1", "S2"],
        "engagement_score": [85.0, 20.0],
        "days_since_last_activity": [2, 45],
        "quiz_pass_rate": [90.0, 30.0],
        "course_progress": [80.0, 15.0]
    })
    enriched = apply_vectorized_transformations(df)

    assert "dropout_risk_score" in enriched.columns
    assert "risk_tier" in enriched.columns
    assert "normalized_engagement" in enriched.columns
    assert "standardized_progress" in enriched.columns
    assert enriched.at[0, "risk_tier"] == "Low"


def test_benchmark_vectorized_vs_iterative():
    """Test execution speed benchmark and numerical equivalence."""
    res = benchmark_vectorized_vs_iterative(n_records=2000)

    assert res["numerical_parity"] is True
    assert res["speedup_factor"] > 1.0  # Vectorized is strictly faster

"""
Unit tests for Assignment 26: Customer Feature Engineering Pipeline.

Covers all 5 task categories:
  Task 1 - Ratio feature computation
  Task 2 - Equal-width engagement tier binning  (pd.cut)
  Task 3 - Quantile-based spend binning         (pd.qcut)
  Task 4 - RFM composite score construction
  Task 5 - Feature validation report
"""

import pytest
import numpy as np
import pandas as pd

from scripts.customer_feature_engineering import (
    create_customer_dataset,
    task1_compute_ratio_features,
    task2_engagement_tier,
    task3_spend_quartile,
    task4_rfm_score,
    task5_validate_features,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def df_raw():
    """200-row customer dataset with well-spread values (reproducible seed)."""
    rng = np.random.default_rng(99)
    n = 200
    return pd.DataFrame({
        "customer_id":             [f"C{str(i).zfill(3)}" for i in range(1, n + 1)],
        "total_transactions":      rng.integers(1, 201, size=n).tolist(),
        "days_as_customer":        rng.integers(30, 1826, size=n).tolist(),
        "total_spent":             rng.uniform(50.0, 50000.0, size=n).round(2).tolist(),
        "days_since_last_purchase": rng.integers(1, 366, size=n).tolist(),
        "purchase_count":          rng.integers(1, 501, size=n).tolist(),
    })


@pytest.fixture
def df_with_ratios(df_raw):
    return task1_compute_ratio_features(df_raw)


@pytest.fixture
def df_with_tiers(df_with_ratios):
    return task2_engagement_tier(df_with_ratios)


@pytest.fixture
def df_with_quartiles(df_with_tiers):
    return task3_spend_quartile(df_with_tiers)


@pytest.fixture
def df_full(df_with_quartiles):
    return task4_rfm_score(df_with_quartiles)


# ---------------------------------------------------------------------------
# Dataset generation
# ---------------------------------------------------------------------------

class TestDatasetGeneration:
    def test_row_count(self):
        df = create_customer_dataset(n=1000)
        assert len(df) == 1000

    def test_unique_customer_ids(self):
        df = create_customer_dataset(n=1000)
        assert df["customer_id"].nunique() == 1000

    def test_required_columns_present(self):
        df = create_customer_dataset(n=500)
        for col in [
            "customer_id", "total_transactions", "days_as_customer",
            "total_spent", "days_since_last_purchase", "purchase_count",
        ]:
            assert col in df.columns

    def test_days_as_customer_minimum(self):
        """Customers should have been registered for at least 30 days."""
        df = create_customer_dataset(n=1000)
        assert df["days_as_customer"].min() >= 30

    def test_total_transactions_positive(self):
        df = create_customer_dataset(n=1000)
        assert (df["total_transactions"] > 0).all()

    def test_total_spent_positive(self):
        df = create_customer_dataset(n=1000)
        assert (df["total_spent"] > 0).all()

    def test_days_since_last_purchase_positive(self):
        df = create_customer_dataset(n=1000)
        assert (df["days_since_last_purchase"] > 0).all()

    def test_custom_row_count(self):
        df = create_customer_dataset(n=250)
        assert len(df) == 250


# ---------------------------------------------------------------------------
# Task 1 — Ratio features
# ---------------------------------------------------------------------------

class TestTask1RatioFeatures:
    def test_returns_dataframe(self, df_raw):
        result = task1_compute_ratio_features(df_raw)
        assert isinstance(result, pd.DataFrame)

    def test_new_columns_added(self, df_with_ratios):
        for col in [
            "transactions_per_month",
            "avg_spend_per_transaction",
            "lifetime_value_per_month",
        ]:
            assert col in df_with_ratios.columns

    def test_original_columns_preserved(self, df_raw, df_with_ratios):
        for col in df_raw.columns:
            assert col in df_with_ratios.columns

    def test_transactions_per_month_positive(self, df_with_ratios):
        assert (df_with_ratios["transactions_per_month"] > 0).all()

    def test_avg_spend_per_transaction_positive(self, df_with_ratios):
        assert (df_with_ratios["avg_spend_per_transaction"] > 0).all()

    def test_lifetime_value_per_month_positive(self, df_with_ratios):
        assert (df_with_ratios["lifetime_value_per_month"] > 0).all()

    def test_no_nan_in_ratio_features(self, df_with_ratios):
        cols = [
            "transactions_per_month",
            "avg_spend_per_transaction",
            "lifetime_value_per_month",
        ]
        assert df_with_ratios[cols].isna().sum().sum() == 0

    def test_transactions_per_month_formula(self, df_raw):
        """Spot-check first row against manual calculation."""
        result = task1_compute_ratio_features(df_raw)
        row = df_raw.iloc[0]
        expected = row["total_transactions"] / (row["days_as_customer"] / 30)
        assert abs(result.iloc[0]["transactions_per_month"] - expected) < 1e-9

    def test_avg_spend_formula(self, df_raw):
        result = task1_compute_ratio_features(df_raw)
        row = df_raw.iloc[0]
        expected = row["total_spent"] / row["total_transactions"]
        assert abs(result.iloc[0]["avg_spend_per_transaction"] - expected) < 1e-9

    def test_input_not_mutated(self, df_raw):
        cols_before = list(df_raw.columns)
        task1_compute_ratio_features(df_raw)
        assert list(df_raw.columns) == cols_before


# ---------------------------------------------------------------------------
# Task 2 — Engagement tier binning
# ---------------------------------------------------------------------------

class TestTask2EngagementTier:
    def test_column_created(self, df_with_tiers):
        assert "engagement_tier" in df_with_tiers.columns

    def test_valid_labels_only(self, df_with_tiers):
        valid = {"low", "medium", "high"}
        actual = set(df_with_tiers["engagement_tier"].dropna().astype(str).unique())
        assert actual.issubset(valid)

    def test_all_three_tiers_populated(self, df_with_tiers):
        counts = df_with_tiers["engagement_tier"].value_counts()
        assert len(counts) == 3

    def test_low_tier_transactions_per_month_le_2(self, df_with_tiers):
        low = df_with_tiers[df_with_tiers["engagement_tier"] == "low"]
        assert (low["transactions_per_month"] <= 2).all()

    def test_high_tier_transactions_per_month_gt_10(self, df_with_tiers):
        high = df_with_tiers[df_with_tiers["engagement_tier"] == "high"]
        assert (high["transactions_per_month"] > 10).all()

    def test_medium_tier_in_range(self, df_with_tiers):
        medium = df_with_tiers[df_with_tiers["engagement_tier"] == "medium"]
        assert (medium["transactions_per_month"] > 2).all()
        assert (medium["transactions_per_month"] <= 10).all()

    def test_categorical_dtype(self, df_with_tiers):
        assert str(df_with_tiers["engagement_tier"].dtype) == "category"

    def test_row_count_unchanged(self, df_with_ratios, df_with_tiers):
        assert len(df_with_tiers) == len(df_with_ratios)


# ---------------------------------------------------------------------------
# Task 3 — Spend quartile binning
# ---------------------------------------------------------------------------

class TestTask3SpendQuartile:
    def test_column_created(self, df_with_quartiles):
        assert "spend_quartile" in df_with_quartiles.columns

    def test_valid_labels_only(self, df_with_quartiles):
        valid = {"Q1", "Q2", "Q3", "Q4"}
        actual = set(df_with_quartiles["spend_quartile"].dropna().astype(str).unique())
        assert actual.issubset(valid)

    def test_all_four_quartiles_populated(self, df_with_quartiles):
        counts = df_with_quartiles["spend_quartile"].value_counts()
        assert len(counts) == 4

    def test_quartile_sizes_roughly_equal(self, df_with_quartiles):
        """Each quartile should hold roughly 25 % of customers (±5 %)."""
        counts = df_with_quartiles["spend_quartile"].value_counts()
        n = len(df_with_quartiles)
        for label, cnt in counts.items():
            assert abs(cnt / n - 0.25) < 0.06, f"{label}: {cnt/n:.2%} is not ~25%"

    def test_q1_lowest_spenders(self, df_with_quartiles):
        """Q1 max spend < Q4 min spend."""
        q1_max = df_with_quartiles[df_with_quartiles["spend_quartile"] == "Q1"]["total_spent"].max()
        q4_min = df_with_quartiles[df_with_quartiles["spend_quartile"] == "Q4"]["total_spent"].min()
        assert q1_max < q4_min

    def test_categorical_dtype(self, df_with_quartiles):
        assert str(df_with_quartiles["spend_quartile"].dtype) == "category"

    def test_no_nan_introduced(self, df_with_quartiles):
        assert df_with_quartiles["spend_quartile"].isna().sum() == 0


# ---------------------------------------------------------------------------
# Task 4 — RFM composite score
# ---------------------------------------------------------------------------

class TestTask4RfmScore:
    def test_rfm_columns_created(self, df_full):
        for col in ["recency_score", "frequency_score", "monetary_score", "rfm_score"]:
            assert col in df_full.columns

    def test_rfm_score_range(self, df_full):
        """Composite RFM score must lie within [3, 15]."""
        assert df_full["rfm_score"].min() >= 3
        assert df_full["rfm_score"].max() <= 15

    def test_component_scores_range(self, df_full):
        """Each component quintile score must be 1–5."""
        for col in ["recency_score", "frequency_score", "monetary_score"]:
            scores = df_full[col].astype(int)
            assert scores.min() >= 1
            assert scores.max() <= 5

    def test_recency_score_inverted(self, df_full):
        """Customers with fewer days since purchase should have higher recency scores."""
        low_recency = df_full[df_full["recency_score"].astype(int) == 5]
        high_recency = df_full[df_full["recency_score"].astype(int) == 1]
        assert low_recency["days_since_last_purchase"].mean() < high_recency[
            "days_since_last_purchase"
        ].mean()

    def test_monetary_score_correlated_with_spend(self, df_full):
        """Higher monetary score should correspond to higher total_spent on average."""
        high = df_full[df_full["monetary_score"].astype(int) == 5]
        low = df_full[df_full["monetary_score"].astype(int) == 1]
        assert high["total_spent"].mean() > low["total_spent"].mean()

    def test_rfm_score_is_sum_of_components(self, df_full):
        """Spot-check additive formula for every row."""
        expected = (
            df_full["recency_score"].astype(int)
            + df_full["frequency_score"].astype(int)
            + df_full["monetary_score"].astype(int)
        )
        pd.testing.assert_series_equal(df_full["rfm_score"], expected, check_names=False)

    def test_no_nan_in_rfm_score(self, df_full):
        assert df_full["rfm_score"].isna().sum() == 0


# ---------------------------------------------------------------------------
# Task 5 — Feature validation
# ---------------------------------------------------------------------------

class TestTask5FeatureValidation:
    def test_returns_dict(self, df_full):
        result = task5_validate_features(df_full)
        assert isinstance(result, dict)

    def test_required_keys_present(self, df_full):
        result = task5_validate_features(df_full)
        for key in [
            "engagement_tier_counts",
            "rfm_score_min",
            "rfm_score_max",
            "missing_values",
            "spend_quartile_counts",
        ]:
            assert key in result, f"Missing key: {key}"

    def test_rfm_min_max_in_report(self, df_full):
        result = task5_validate_features(df_full)
        assert result["rfm_score_min"] >= 3
        assert result["rfm_score_max"] <= 15

    def test_no_missing_values_reported(self, df_full):
        result = task5_validate_features(df_full)
        for col, count in result["missing_values"].items():
            assert count == 0, f"Unexpected NaN in {col}: {count}"

    def test_engagement_tier_counts_all_tiers(self, df_full):
        result = task5_validate_features(df_full)
        tier_keys = {str(k) for k in result["engagement_tier_counts"]}
        assert tier_keys == {"low", "medium", "high"}

    def test_spend_quartile_counts_all_quartiles(self, df_full):
        result = task5_validate_features(df_full)
        quartile_keys = {str(k) for k in result["spend_quartile_counts"]}
        assert quartile_keys == {"Q1", "Q2", "Q3", "Q4"}

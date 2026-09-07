"""
Customer Feature Engineering Pipeline (Assignment 26).

Engineers business-meaningful features from raw customer transaction data:
ratio features, equal-width and quantile bins, and a composite RFM score.

Tasks:
  1. Compute ratio features (transactions_per_month, avg_spend_per_transaction,
     lifetime_value_per_month)
  2. Binning with equal-width bins (engagement_tier)
  3. Binning with quantiles (spend_quartile)
  4. Composite RFM score (recency_score, frequency_score, monetary_score, rfm_score)
  5. Feature validation (ranges, distributions, missing values)
"""

import os
import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Synthetic dataset generation
# ---------------------------------------------------------------------------

def create_customer_dataset(n: int = 1000) -> pd.DataFrame:
    """
    Generate n customer records with transaction history metrics.

    Columns:
      total_transactions       - lifetime order count
      days_as_customer         - tenure since first purchase (30–1 825 days)
      total_spent              - cumulative spend (£50–£50 000)
      days_since_last_purchase - recency indicator (1–365 days)
      purchase_count           - distinct purchase events (may differ from
                                 total_transactions when orders have multiple
                                 line items)
    """
    rng = np.random.default_rng(42)
    customer_ids = [f"C{str(i).zfill(4)}" for i in range(1, n + 1)]
    return pd.DataFrame({
        "customer_id":             customer_ids,
        "total_transactions":      rng.integers(1, 201, size=n).tolist(),
        "days_as_customer":        rng.integers(30, 1826, size=n).tolist(),
        "total_spent":             rng.uniform(50.0, 50000.0, size=n).round(2).tolist(),
        "days_since_last_purchase": rng.integers(1, 366, size=n).tolist(),
        "purchase_count":          rng.integers(1, 501, size=n).tolist(),
    })


# ---------------------------------------------------------------------------
# Task 1 — Ratio features
# ---------------------------------------------------------------------------

def task1_compute_ratio_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Derive three rate/ratio features from raw counts and totals.

    transactions_per_month   - purchase frequency normalised to a 30-day window
    avg_spend_per_transaction - average basket size in £
    lifetime_value_per_month  - monthly revenue rate across full tenure
    """
    print("\n" + "=" * 60)
    print("TASK 1: COMPUTE RATIO FEATURES")
    print("=" * 60)

    df = df.copy()
    months_as_customer = df["days_as_customer"] / 30

    df["transactions_per_month"] = df["total_transactions"] / months_as_customer
    df["avg_spend_per_transaction"] = df["total_spent"] / df["total_transactions"]
    df["lifetime_value_per_month"] = df["total_spent"] / months_as_customer

    print(df[["transactions_per_month", "avg_spend_per_transaction"]].describe())
    return df


# ---------------------------------------------------------------------------
# Task 2 — Equal-width binning
# ---------------------------------------------------------------------------

def task2_engagement_tier(df: pd.DataFrame) -> pd.DataFrame:
    """
    Classify customers into three engagement tiers using fixed-width bin edges.

    Bin edges (transactions per month):
      [0, 2)   → 'low'    – infrequent buyers
      [2, 10)  → 'medium' – regular buyers
      [10, ∞)  → 'high'   – power buyers

    pd.cut is used here (not pd.qcut) because the thresholds are business-defined
    domain boundaries, not statistical quantiles.  Equal-width binning ensures the
    same interpretation across different time periods or customer cohorts.
    """
    print("\n" + "=" * 60)
    print("TASK 2: BINNING WITH EQUAL-WIDTH BINS (engagement_tier)")
    print("=" * 60)

    df = df.copy()
    df["engagement_tier"] = pd.cut(
        df["transactions_per_month"],
        bins=[0, 2, 10, float("inf")],
        labels=["low", "medium", "high"],
    )

    print(df["engagement_tier"].value_counts())
    return df


# ---------------------------------------------------------------------------
# Task 3 — Quantile binning
# ---------------------------------------------------------------------------

def task3_spend_quartile(df: pd.DataFrame) -> pd.DataFrame:
    """
    Assign spend quartile labels using quantile-based bin edges.

    pd.qcut is used here (not pd.cut) because the goal is equal-sized groups —
    each quartile contains ~25 % of customers regardless of spend distribution
    skew.  This makes downstream segment sizes comparable for campaign planning.
    """
    print("\n" + "=" * 60)
    print("TASK 3: BINNING WITH QUANTILES (spend_quartile)")
    print("=" * 60)

    df = df.copy()
    df["spend_quartile"] = pd.qcut(
        df["total_spent"],
        q=4,
        labels=["Q1", "Q2", "Q3", "Q4"],
    )

    print(df["spend_quartile"].value_counts())
    return df


# ---------------------------------------------------------------------------
# Task 4 — RFM composite score
# ---------------------------------------------------------------------------

def task4_rfm_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build a composite RFM (Recency–Frequency–Monetary) score.

    Each dimension is scored 1–5 using quintile bins:
      recency_score  – inverted (5 = most recent; shorter gap is better)
      frequency_score – normal (5 = highest purchase count)
      monetary_score  – normal (5 = highest total spend)

    rfm_score = sum of three quintile scores → range [3, 15].

    Scoring via pd.qcut ensures each quintile band contains equal customer
    counts, making the composite score distribution symmetric and comparable
    across time snapshots.
    """
    print("\n" + "=" * 60)
    print("TASK 4: COMPOSITE RFM SCORE")
    print("=" * 60)

    df = df.copy()

    df["recency_score"] = pd.qcut(
        df["days_since_last_purchase"], q=5, labels=[5, 4, 3, 2, 1]
    )
    df["frequency_score"] = pd.qcut(
        df["purchase_count"], q=5, labels=[1, 2, 3, 4, 5]
    )
    df["monetary_score"] = pd.qcut(
        df["total_spent"], q=5, labels=[1, 2, 3, 4, 5]
    )

    df["rfm_score"] = (
        df["recency_score"].astype(int)
        + df["frequency_score"].astype(int)
        + df["monetary_score"].astype(int)
    )

    print(f"RFM Score Distribution:\n{df['rfm_score'].describe()}")
    return df


# ---------------------------------------------------------------------------
# Task 5 — Feature validation
# ---------------------------------------------------------------------------

def task5_validate_features(df: pd.DataFrame) -> dict:
    """
    Validate all engineered features for sensible ranges and zero data leakage.

    Checks:
      - engagement_tier distribution (all three labels populated)
      - RFM score range is within [3, 15]
      - No NaN values introduced by the engineered features
      - All ratio features are strictly positive
    """
    print("\n" + "=" * 60)
    print("TASK 5: FEATURE VALIDATION")
    print("=" * 60)

    print(f"Engagement tier distribution:\n{df['engagement_tier'].value_counts()}")
    print(f"RFM score range: {df['rfm_score'].min()}-{df['rfm_score'].max()}")

    missing = df[["engagement_tier", "spend_quartile", "rfm_score"]].isna().sum()
    print(f"Missing values:\n{missing}")

    ratio_features = [
        "transactions_per_month",
        "avg_spend_per_transaction",
        "lifetime_value_per_month",
    ]
    for feat in ratio_features:
        neg_count = (df[feat] <= 0).sum()
        print(f"  {feat} non-positive count: {neg_count}")

    return {
        "engagement_tier_counts": df["engagement_tier"].value_counts().to_dict(),
        "rfm_score_min":          int(df["rfm_score"].min()),
        "rfm_score_max":          int(df["rfm_score"].max()),
        "missing_values":         missing.to_dict(),
        "spend_quartile_counts":  df["spend_quartile"].value_counts().to_dict(),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("CUSTOMER FEATURE ENGINEERING PIPELINE")
    print("=" * 60)

    df = create_customer_dataset(n=1000)
    print(f"\nDataset: {len(df)} rows x {len(df.columns)} cols")
    print(f"Columns: {list(df.columns)}")

    df = task1_compute_ratio_features(df)
    df = task2_engagement_tier(df)
    df = task3_spend_quartile(df)
    df = task4_rfm_score(df)
    validation = task5_validate_features(df)

    os.makedirs("output", exist_ok=True)
    df.to_csv("output/customer_features.csv", index=False)
    print("\n  Saved: output/customer_features.csv")

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)
    print("  output/customer_features.csv")

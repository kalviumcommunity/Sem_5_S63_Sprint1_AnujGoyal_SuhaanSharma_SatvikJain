"""
Outlier Detection and Handling Pipeline for Customer Revenue Data.

Detects extreme values using both Z-score and IQR methods, applies
per-column handling strategies (cap / flag / remove), and writes a
full cleaning log for auditability.

Tasks:
  1. Z-score outlier detection  (scipy.stats.zscore, threshold +-3)
  2. IQR outlier detection       (1.5 x IQR fence)
  3. Cap outliers at IQR bounds  (clip to lower/upper fence)
  4. Flag outliers with binary column (combined Z + IQR mask)
  5. Cleaning log                (CSV audit trail of every decision)
"""

import os
import json
import numpy as np
import pandas as pd
from scipy import stats

# ---------------------------------------------------------------------------
# Synthetic customer revenue dataset
# ---------------------------------------------------------------------------

def create_customer_dataset(n: int = 200) -> pd.DataFrame:
    """
    Generate customer records with intentional outliers injected.

    Injected problems:
      revenue : one whale customer ($98 000), one data-entry error ($0.01)
      age     : two impossible ages (155, 172) and one borderline (0)
      sessions: a few extreme engagement counts
    """
    rng = np.random.default_rng(42)

    customer_ids = [f"CUST{str(i).zfill(4)}" for i in range(1, n + 1)]

    # Normal revenue: $50 - $2 000
    revenue = rng.uniform(50, 2000, size=n).round(2)

    # Normal age: 18-70
    age = rng.integers(18, 70, size=n).astype(float)

    # Normal sessions per month: 1-30
    sessions = rng.integers(1, 30, size=n).astype(float)

    df = pd.DataFrame({
        "customer_id": customer_ids,
        "revenue":     revenue,
        "age":         age,
        "sessions":    sessions,
    })

    # Inject revenue outliers
    df.loc[0,   "revenue"] = 98_000.00   # extreme high (whale)
    df.loc[1,   "revenue"] = 0.01        # extreme low  (data entry error)
    df.loc[2,   "revenue"] = 45_000.00   # high outlier
    df.loc[3,   "revenue"] = 55_000.00   # high outlier

    # Inject impossible ages
    df.loc[10,  "age"] = 155.0
    df.loc[11,  "age"] = 172.0
    df.loc[12,  "age"] = 0.0             # impossible: age = 0

    # Inject session outliers
    df.loc[20,  "sessions"] = 500.0
    df.loc[21,  "sessions"] = 450.0

    return df


# ---------------------------------------------------------------------------
# Task 1 -- Z-score outlier detection
# ---------------------------------------------------------------------------

Z_THRESHOLD = 3.0


def detect_zscore_outliers(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    """
    Flag values beyond +-3 standard deviations using scipy.stats.zscore.

    Z-score = (x - mean) / std
    Assumption: the column is approximately normally distributed.
    Works best on symmetric distributions; misleads on heavy-tailed or
    skewed data because the mean and std are pulled by the outliers themselves.
    """
    print("\n" + "=" * 60)
    print("TASK 1: Z-SCORE OUTLIER DETECTION")
    print("=" * 60)
    print(f"Threshold: |Z| > {Z_THRESHOLD}  (beyond +-3 standard deviations)\n")

    for col in columns:
        z_col = f"{col}_zscore"
        flag_col = f"{col}_zscore_outlier"

        # scipy zscore ignores NaN with nan_policy='omit'
        z_vals = np.abs(stats.zscore(df[col].dropna()))
        z_series = pd.Series(z_vals, index=df[col].dropna().index)
        df[z_col] = z_series.reindex(df.index)           # NaN stays NaN

        df[flag_col] = (df[z_col] > Z_THRESHOLD).astype(int)

        outliers = df[df[flag_col] == 1]

        print(f"Column: {col}")
        print(f"  Mean:          {df[col].mean():>12.2f}")
        print(f"  Std dev:       {df[col].std():>12.2f}")
        print(f"  Z-score range: {df[z_col].min():.2f} to {df[z_col].max():.2f}")
        print(f"  Outliers (|Z|>{Z_THRESHOLD}): {len(outliers)}  "
              f"({len(outliers)/len(df)*100:.1f}% of rows)")

        if not outliers.empty:
            print(f"  Outlier values: {sorted(outliers[col].tolist())}")

        print()

    return df


# ---------------------------------------------------------------------------
# Task 2 -- IQR outlier detection
# ---------------------------------------------------------------------------

IQR_MULTIPLIER = 1.5


def detect_iqr_outliers(df: pd.DataFrame, columns: list) -> tuple:
    """
    Flag values beyond 1.5 x IQR from Q1/Q3.

    IQR fence:
      Lower = Q1 - 1.5 * IQR
      Upper = Q3 + 1.5 * IQR

    The 1.5 multiplier comes from Tukey (1977).  Under a normal distribution
    it captures 99.3% of the data -- roughly equivalent to +-2.7 sigma.
    A 3.0 multiplier (extreme outlier fence) captures ~99.99% of normal data.

    IQR advantage over Z-score: based on percentiles so not distorted by the
    very outliers it is trying to find.  Better for skewed distributions.
    """
    print("\n" + "=" * 60)
    print("TASK 2: IQR OUTLIER DETECTION")
    print("=" * 60)
    print(f"Multiplier: {IQR_MULTIPLIER} x IQR  (Tukey fence)\n")

    bounds = {}

    for col in columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - IQR_MULTIPLIER * IQR
        upper = Q3 + IQR_MULTIPLIER * IQR

        flag_col = f"{col}_iqr_outlier"
        df[flag_col] = ((df[col] < lower) | (df[col] > upper)).astype(int)

        outliers = df[df[flag_col] == 1]

        bounds[col] = {"Q1": Q1, "Q3": Q3, "IQR": IQR,
                       "lower": lower, "upper": upper}

        print(f"Column: {col}")
        print(f"  Q1:    {Q1:>10.2f}")
        print(f"  Q3:    {Q3:>10.2f}")
        print(f"  IQR:   {IQR:>10.2f}")
        print(f"  Lower fence: {lower:>10.2f}")
        print(f"  Upper fence: {upper:>10.2f}")
        print(f"  Outliers:    {len(outliers)}  "
              f"({len(outliers)/len(df)*100:.1f}% of rows)")

        if not outliers.empty:
            print(f"  Outlier values: {sorted(outliers[col].tolist())}")

        print()

    return df, bounds


# ---------------------------------------------------------------------------
# Task 3 -- Cap outliers at IQR boundaries
# ---------------------------------------------------------------------------

def cap_outliers(df: pd.DataFrame, columns: list, bounds: dict) -> pd.DataFrame:
    """
    Apply Winsorization: replace values outside the IQR fence with the fence value.

    Why cap instead of remove?
      - Removal loses the record entirely -- the customer existed, the event happened.
      - Capping preserves row count and keeps the signal (this WAS an outlier)
        while limiting its distorting effect on aggregations.
      - Best for: revenue, sessions, engagement counts.
      - Not appropriate for: impossible values (age=155) which should be nulled/removed.
    """
    print("\n" + "=" * 60)
    print("TASK 3: CAP OUTLIERS AT IQR BOUNDARIES (WINSORIZATION)")
    print("=" * 60)

    for col in columns:
        b = bounds[col]
        capped_col = f"{col}_capped"

        df[capped_col] = df[col].clip(lower=b["lower"], upper=b["upper"])

        n_capped_low  = (df[col] < b["lower"]).sum()
        n_capped_high = (df[col] > b["upper"]).sum()

        print(f"Column: {col}")
        print(f"  Before cap  ->  min: {df[col].min():>12.2f}  "
              f"max: {df[col].max():>12.2f}")
        print(f"  After cap   ->  min: {df[capped_col].min():>12.2f}  "
              f"max: {df[capped_col].max():>12.2f}")
        print(f"  Values capped low:  {n_capped_low}")
        print(f"  Values capped high: {n_capped_high}")
        print(f"  Mean before cap: {df[col].mean():.2f}  "
              f"  Mean after cap: {df[capped_col].mean():.2f}")
        print()

    return df


# ---------------------------------------------------------------------------
# Task 4 -- Flag outliers with a combined binary column
# ---------------------------------------------------------------------------

def flag_combined_outliers(df: pd.DataFrame, columns: list) -> tuple:
    """
    Combine Z-score and IQR flags into a single is_outlier column per column.

    Flagging strategy (preferred over removal) because:
      - Keeps every record in the dataset -- no information loss.
      - Downstream models can decide to weight, exclude, or inspect separately.
      - Maintains audit trail: WHERE the outlier was found is preserved.
      - Removal is irreversible; a flag can always be ignored.

    Combined rule: outlier if flagged by EITHER method (union = more conservative).
    """
    print("\n" + "=" * 60)
    print("TASK 4: COMBINED OUTLIER FLAG")
    print("=" * 60)
    print("Logic: is_outlier = (IQR flag == 1) OR (Z-score flag == 1)\n")

    split_info = {}

    for col in columns:
        z_flag   = f"{col}_zscore_outlier"
        iqr_flag = f"{col}_iqr_outlier"
        out_flag = f"{col}_is_outlier"

        z_available   = z_flag   in df.columns
        iqr_available = iqr_flag in df.columns

        if z_available and iqr_available:
            df[out_flag] = ((df[z_flag] == 1) | (df[iqr_flag] == 1)).astype(int)
        elif iqr_available:
            df[out_flag] = df[iqr_flag]
        elif z_available:
            df[out_flag] = df[z_flag]
        else:
            df[out_flag] = 0

        normal    = df[df[out_flag] == 0]
        anomalies = df[df[out_flag] == 1]

        split_info[col] = {
            "normal_count":   len(normal),
            "outlier_count":  len(anomalies),
        }

        print(f"Column: {col}")
        print(f"  Normal records:   {len(normal)}")
        print(f"  Outlier records:  {len(anomalies)}  "
              f"({len(anomalies)/len(df)*100:.1f}%)")
        if not anomalies.empty:
            print(f"  Flagged values:   "
                  f"{sorted(anomalies[col].tolist())}")
        print()

    # Overall combined flag (any column has an outlier)
    all_flags = [f"{c}_is_outlier" for c in columns if f"{c}_is_outlier" in df.columns]
    df["any_outlier"] = df[all_flags].max(axis=1)

    total_normal    = (df["any_outlier"] == 0).sum()
    total_anomalies = (df["any_outlier"] == 1).sum()

    print(f"OVERALL:")
    print(f"  Clean records (no outlier in any column): {total_normal}")
    print(f"  Records with at least one outlier:        {total_anomalies}")

    return df, split_info


# ---------------------------------------------------------------------------
# Task 5 -- Cleaning log
# ---------------------------------------------------------------------------

def build_cleaning_log(
    df: pd.DataFrame,
    columns: list,
    bounds: dict,
    split_info: dict,
) -> pd.DataFrame:
    """
    Document every outlier-handling decision in a structured audit log.

    One row per column per method, recording:
      - detection method and thresholds used
      - action taken and business justification
      - number of rows affected
      - timestamp for reproducibility
    """
    print("\n" + "=" * 60)
    print("TASK 5: CLEANING LOG")
    print("=" * 60)

    # Business decisions per column
    decisions = {
        "revenue": {
            "action": "cap",
            "justification": (
                "Revenue outliers (whale customers, data-entry errors) are real "
                "events but distort mean-based metrics. Capping at IQR fence "
                "preserves row count while limiting distributional distortion. "
                "The original value is kept in 'revenue' for reference."
            ),
        },
        "age": {
            "action": "flag_and_null",
            "justification": (
                "Ages >120 or <=0 are physically impossible; they represent "
                "data entry errors. Flagged and nulled rather than capped "
                "because a 'capped' impossible age would still be wrong."
            ),
        },
        "sessions": {
            "action": "cap",
            "justification": (
                "Extreme session counts likely reflect bot traffic or test "
                "accounts. Capping limits their impact on engagement averages "
                "without deleting the customer record."
            ),
        },
    }

    log_rows = []
    ts = pd.Timestamp.now().isoformat(timespec="seconds")

    for col in columns:
        b = bounds.get(col, {})
        si = split_info.get(col, {})
        dec = decisions.get(col, {"action": "flag", "justification": "Default: flag only"})

        # IQR log entry
        log_rows.append({
            "timestamp":        ts,
            "column":           col,
            "method":           "IQR",
            "threshold_lower":  round(b.get("lower", float("nan")), 4),
            "threshold_upper":  round(b.get("upper", float("nan")), 4),
            "q1":               round(b.get("Q1", float("nan")), 4),
            "q3":               round(b.get("Q3", float("nan")), 4),
            "iqr":              round(b.get("IQR", float("nan")), 4),
            "multiplier":       IQR_MULTIPLIER,
            "action":           dec["action"],
            "affected_rows":    int(si.get("outlier_count", 0)),
            "total_rows":       len(df),
            "pct_affected":     round(si.get("outlier_count", 0) / len(df) * 100, 2),
            "justification":    dec["justification"],
        })

        # Z-score log entry
        z_col = f"{col}_zscore"
        if z_col in df.columns:
            z_outlier_count = int((df[f"{col}_zscore_outlier"] == 1).sum()) \
                              if f"{col}_zscore_outlier" in df.columns else 0
            log_rows.append({
                "timestamp":        ts,
                "column":           col,
                "method":           "Z-score",
                "threshold_lower":  -Z_THRESHOLD,
                "threshold_upper":  Z_THRESHOLD,
                "q1":               "",
                "q3":               "",
                "iqr":              "",
                "multiplier":       "",
                "action":           dec["action"],
                "affected_rows":    z_outlier_count,
                "total_rows":       len(df),
                "pct_affected":     round(z_outlier_count / len(df) * 100, 2),
                "justification":    dec["justification"],
            })

    log_df = pd.DataFrame(log_rows)

    print("Cleaning log entries:")
    print(log_df[["column", "method", "action", "affected_rows", "pct_affected",
                   "threshold_lower", "threshold_upper"]].to_string(index=False))

    os.makedirs("output", exist_ok=True)
    log_df.to_csv("output/cleaning_log.csv", index=False)
    print("\nFull cleaning log saved to output/cleaning_log.csv")

    return log_df


# ---------------------------------------------------------------------------
# Domain-rule enforcement (age column special case)
# ---------------------------------------------------------------------------

def enforce_domain_rules(df: pd.DataFrame) -> pd.DataFrame:
    """
    Null out physically impossible values that IQR/Z-score alone may miss.

    Domain rules:
      age      : must be 0 < age <= 120
      sessions : must be >= 1
    """
    print("\n" + "=" * 60)
    print("DOMAIN RULE ENFORCEMENT (impossible values)")
    print("=" * 60)

    age_impossible = (df["age"] <= 0) | (df["age"] > 120)
    n_age_bad = age_impossible.sum()
    if n_age_bad > 0:
        print(f"age: {n_age_bad} impossible value(s) found -> "
              f"{df.loc[age_impossible, 'age'].tolist()}")
        df.loc[age_impossible, "age"] = np.nan
        df.loc[age_impossible, "age_iqr_outlier"]    = 1
        df.loc[age_impossible, "age_zscore_outlier"] = 1
        print(f"  Action: set to NaN (domain violation)")

    sessions_bad = df["sessions"] < 1
    n_sess_bad = sessions_bad.sum()
    if n_sess_bad > 0:
        print(f"sessions: {n_sess_bad} value(s) below minimum -> "
              f"{df.loc[sessions_bad, 'sessions'].tolist()}")
        df.loc[sessions_bad, "sessions"] = np.nan

    return df


# ---------------------------------------------------------------------------
# Pipeline summary
# ---------------------------------------------------------------------------

def print_summary(df_raw: pd.DataFrame, df: pd.DataFrame, log_df: pd.DataFrame):
    print("\n" + "=" * 60)
    print("PIPELINE SUMMARY")
    print("=" * 60)
    print(f"Total rows:            {len(df)}")
    print(f"Columns analyzed:      revenue, age, sessions")
    print(f"Log entries written:   {len(log_df)}")
    print(f"Output files:")
    print(f"  output/cleaning_log.csv")
    print(f"  output/outlier_summary.csv")

    print("\nPer-column before/after stats:")
    for col in ["revenue", "age", "sessions"]:
        capped = f"{col}_capped"
        after_col = df[capped] if capped in df.columns else df[col]
        print(f"\n  {col}")
        print(f"    Raw    -> mean={df_raw[col].mean():.2f}  "
              f"std={df_raw[col].std():.2f}  "
              f"max={df_raw[col].max():.2f}")
        print(f"    Cleaned-> mean={after_col.mean():.2f}  "
              f"std={after_col.std():.2f}  "
              f"max={after_col.max():.2f}")

    # comparison for all flagged columns
    flag_cols = [c for c in df.columns if c.endswith("_is_outlier")]
    print(f"\nOutlier flags created: {flag_cols}")
    if "any_outlier" in df.columns:
        print(f"Records with ANY outlier: {df['any_outlier'].sum()}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

TARGET_COLUMNS = ["revenue", "age", "sessions"]

if __name__ == "__main__":
    print("=" * 60)
    print("OUTLIER DETECTION AND HANDLING PIPELINE")
    print("Customer Revenue Dataset")
    print("=" * 60)

    # Build dataset
    df_raw = create_customer_dataset(n=200)
    df = df_raw.copy()

    print(f"\nDataset: {len(df)} rows x {len(df.columns)} columns")
    print(f"\nRaw descriptive statistics:")
    print(df[TARGET_COLUMNS].describe().round(2).to_string())

    print("\nKnown injected outliers (first 25 rows sample):")
    print(df[TARGET_COLUMNS].head(25).to_string())

    # Task 1 -- Z-score
    df = detect_zscore_outliers(df, TARGET_COLUMNS)

    # Task 2 -- IQR
    df, bounds = detect_iqr_outliers(df, TARGET_COLUMNS)

    # Domain rule enforcement (nulls impossible ages before capping)
    df = enforce_domain_rules(df)

    # Task 3 -- Cap
    df = cap_outliers(df, TARGET_COLUMNS, bounds)

    # Task 4 -- Combined flag
    df, split_info = flag_combined_outliers(df, TARGET_COLUMNS)

    # Task 5 -- Cleaning log
    log_df = build_cleaning_log(df, TARGET_COLUMNS, bounds, split_info)

    # Save outlier summary
    os.makedirs("output", exist_ok=True)
    summary_cols = (
        ["customer_id"] + TARGET_COLUMNS
        + [f"{c}_zscore" for c in TARGET_COLUMNS]
        + [f"{c}_is_outlier" for c in TARGET_COLUMNS]
        + [f"{c}_capped" for c in TARGET_COLUMNS]
        + ["any_outlier"]
    )
    summary_cols = [c for c in summary_cols if c in df.columns]
    df[summary_cols].to_csv("output/outlier_summary.csv", index=False)

    # Pipeline summary
    print_summary(df_raw, df, log_df)
    print("\nDone. All outputs written to output/")

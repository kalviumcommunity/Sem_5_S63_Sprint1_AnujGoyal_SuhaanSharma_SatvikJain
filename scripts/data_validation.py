"""
Data Validation Rules Pipeline for Customer Campaign Data.

Validates raw records before analysis by applying 5 categories of rules,
isolating failures, and producing a structured validation report.

Tasks:
  1. Range Checks          (age 0-150, price >= 0, birth_date 1920-today)
  2. Null Constraints      (customer_id, email must be present)
  3. Format Pattern        (email must contain @, phone must be 10 digits)
  4. Business Rule         (campaign_end_date >= campaign_start_date)
  5. Validation Report     (passes_all_checks, failures CSV, summary stats)
"""

import os
import re
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Synthetic customer campaign dataset
# ---------------------------------------------------------------------------

def create_campaign_dataset(n: int = 150) -> pd.DataFrame:
    """
    Generate customer campaign records with intentional data quality problems.

    Injected problems:
      birth_date      : 5 records set in year 2050 (impossible future date)
      price           : 4 records with negative values (data-entry errors)
      customer_id     : 6 records set to NaN (missing required identifier)
      campaign dates  : 5 records where end_date < start_date (logical violation)
      email           : 4 records missing @ symbol (invalid format)
      phone           : 5 records that are not 10 digits (invalid format)
    """
    rng = np.random.default_rng(0)

    customer_ids = [f"CUST{str(i).zfill(4)}" for i in range(1, n + 1)]
    ages = rng.integers(18, 75, size=n).tolist()
    prices = rng.uniform(10.0, 500.0, size=n).round(2).tolist()

    # Generate valid birth years (1950-2005)
    birth_years = rng.integers(1950, 2005, size=n)
    birth_months = rng.integers(1, 13, size=n)
    birth_days = rng.integers(1, 29, size=n)
    birth_dates = [
        f"{y}-{m:02d}-{d:02d}" for y, m, d in zip(birth_years, birth_months, birth_days)
    ]

    # Generate valid campaign date pairs (start then end, always ordered)
    start_years = rng.integers(2023, 2026, size=n)
    start_months = rng.integers(1, 13, size=n)
    start_days = rng.integers(1, 25, size=n)
    end_offsets = rng.integers(7, 90, size=n)

    campaign_start = pd.to_datetime([
        f"{y}-{m:02d}-{d:02d}" for y, m, d in zip(start_years, start_months, start_days)
    ])
    campaign_end = campaign_start + pd.to_timedelta(end_offsets, unit="D")

    emails = [f"user{i}@example.com" for i in range(1, n + 1)]
    phones = [f"{rng.integers(1000000000, 9999999999):010d}" for _ in range(n)]

    df = pd.DataFrame({
        "customer_id":      customer_ids,
        "age":              ages,
        "price":            prices,
        "birth_date":       pd.to_datetime(birth_dates),
        "campaign_start":   campaign_start,
        "campaign_end":     campaign_end,
        "email":            emails,
        "phone":            phones,
    })

    # --- Inject Rule 1 violations: birth_date in future year 2050 ---
    for idx in [5, 15, 30, 60, 90]:
        df.loc[idx, "birth_date"] = pd.Timestamp("2050-06-15")

    # --- Inject Rule 2 violations: negative price ---
    for idx in [2, 20, 50, 80]:
        df.loc[idx, "price"] = -abs(df.loc[idx, "price"])

    # --- Inject Rule 3 violations: missing customer_id ---
    for idx in [0, 10, 25, 45, 70, 110]:
        df.loc[idx, "customer_id"] = np.nan

    # --- Inject Rule 4 violations: end_date before start_date ---
    for idx in [3, 18, 35, 55, 95]:
        df.loc[idx, "campaign_end"] = df.loc[idx, "campaign_start"] - pd.Timedelta(days=5)

    # --- Inject Rule 5 violations: invalid email (no @) ---
    for idx in [7, 22, 40, 100]:
        df.loc[idx, "email"] = f"user{idx}example.com"

    # --- Inject Rule 6 violations: phone not 10 digits ---
    for idx in [4, 14, 33, 65, 120]:
        df.loc[idx, "phone"] = "555-ABC"

    return df


# ---------------------------------------------------------------------------
# Task 1 — Range Checks
# ---------------------------------------------------------------------------

def apply_range_checks(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validates numerical and date values fall within acceptable ranges.

    Rules:
      valid_age       : 0 <= age <= 150
      valid_price     : price >= 0
      valid_birth_date: 1920-01-01 <= birth_date <= today
    """
    print("\n" + "=" * 60)
    print("TASK 1: RANGE CHECKS")
    print("=" * 60)

    df["valid_age"] = (df["age"] >= 0) & (df["age"] <= 150)
    df["valid_price"] = df["price"] >= 0
    df["valid_birth_date"] = (
        (df["birth_date"] >= pd.Timestamp("1920-01-01")) &
        (df["birth_date"] <= pd.Timestamp.now())
    )

    print(f"  Invalid ages       : {(~df['valid_age']).sum()}")
    print(f"  Negative prices    : {(~df['valid_price']).sum()}")
    print(f"  Future birth_dates : {(~df['valid_birth_date']).sum()}")

    return df


# ---------------------------------------------------------------------------
# Task 2 — Null Constraints
# ---------------------------------------------------------------------------

def apply_null_constraints(df: pd.DataFrame) -> pd.DataFrame:
    """
    Checks that required identifier and contact fields are not null.

    Rules:
      valid_customer_id : customer_id must not be NaN
      valid_email_null  : email must not be NaN
    """
    print("\n" + "=" * 60)
    print("TASK 2: NULL CONSTRAINTS")
    print("=" * 60)

    df["valid_customer_id"] = df["customer_id"].notna()
    df["valid_email_null"] = df["email"].notna()

    print(f"  Missing customer_id: {(~df['valid_customer_id']).sum()}")
    print(f"  Missing email      : {(~df['valid_email_null']).sum()}")

    return df


# ---------------------------------------------------------------------------
# Task 3 — Format Pattern Validation
# ---------------------------------------------------------------------------

def apply_format_checks(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validates string fields against expected formats using regex patterns.

    Rules:
      valid_email_format: email must contain '@' (basic sanity check)
      valid_phone       : phone must be exactly 10 consecutive digits
    """
    print("\n" + "=" * 60)
    print("TASK 3: FORMAT PATTERN VALIDATION")
    print("=" * 60)

    df["valid_email_format"] = df["email"].str.contains("@", na=False)
    df["valid_phone"] = df["phone"].str.match(r"^\d{10}$", na=False)

    print(f"  Invalid email format: {(~df['valid_email_format']).sum()}")
    print(f"  Invalid phone format: {(~df['valid_phone']).sum()}")

    return df


# ---------------------------------------------------------------------------
# Task 4 — Business Rule Validation
# ---------------------------------------------------------------------------

def apply_business_rules(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enforces domain-level logical constraints between columns.

    Rules:
      valid_date_order: campaign_end >= campaign_start (end cannot precede start)
    """
    print("\n" + "=" * 60)
    print("TASK 4: BUSINESS RULE VALIDATION")
    print("=" * 60)

    df["valid_date_order"] = df["campaign_end"] >= df["campaign_start"]

    print(f"  Invalid date ranges (end before start): {(~df['valid_date_order']).sum()}")

    return df


# ---------------------------------------------------------------------------
# Task 5 — Validation Report
# ---------------------------------------------------------------------------

VALIDATION_COLS = [
    "valid_age",
    "valid_price",
    "valid_birth_date",
    "valid_customer_id",
    "valid_email_format",
    "valid_phone",
    "valid_date_order",
]


def build_validation_report(df: pd.DataFrame) -> tuple:
    """
    Aggregates all rule flags into a master pass/fail column, isolates
    failures, exports them to CSV, and prints a structured summary report.

    Returns:
      (df_with_flags, failures_df, report_dict)
    """
    print("\n" + "=" * 60)
    print("TASK 5: VALIDATION REPORT")
    print("=" * 60)

    df["passes_all_checks"] = df[VALIDATION_COLS].all(axis=1)

    total = len(df)
    passed = int(df["passes_all_checks"].sum())
    failed = int((~df["passes_all_checks"]).sum())

    # Isolate failures
    failures = df[~df["passes_all_checks"]].copy()

    os.makedirs("output", exist_ok=True)
    failures.to_csv("output/validation_failures.csv", index=False)

    # Per-rule failure counts
    rule_summary = {}
    for col in VALIDATION_COLS:
        rule_name = col.replace("valid_", "")
        fail_count = int((~df[col]).sum())
        pct = round(fail_count / total * 100, 2)
        rule_summary[rule_name] = {"failures": fail_count, "pct": pct}

    report = {
        "total_records":  total,
        "passed":         passed,
        "failed":         failed,
        "pass_rate_pct":  round(passed / total * 100, 2),
        "rules":          rule_summary,
    }

    # Print structured report
    print(f"\n  Total records   : {total}")
    print(f"  Passed all rules: {passed}  ({report['pass_rate_pct']}%)")
    print(f"  Failed           : {failed}")
    print(f"\n  Failures by rule:")
    for rule, stats in rule_summary.items():
        bar = "#" * stats["failures"]
        print(f"    {rule:<22}: {stats['failures']:>3} ({stats['pct']:>5.1f}%)  {bar}")

    print(f"\n  Failure records saved to: output/validation_failures.csv")

    return df, failures, report


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("DATA VALIDATION RULES PIPELINE")
    print("Customer Campaign Dataset")
    print("=" * 60)

    df_raw = create_campaign_dataset(n=150)
    df = df_raw.copy()

    print(f"\nDataset: {len(df)} rows x {len(df.columns)} columns")
    print("\nSample of intentionally corrupted records:")
    sample_cols = ["customer_id", "age", "price", "birth_date",
                   "campaign_start", "campaign_end", "email", "phone"]
    bad_idx = [0, 2, 3, 4, 5, 7]
    print(df.loc[bad_idx, sample_cols].to_string())

    df = apply_range_checks(df)
    df = apply_null_constraints(df)
    df = apply_format_checks(df)
    df = apply_business_rules(df)
    df, failures, report = build_validation_report(df)

    df_clean = df[df["passes_all_checks"]].copy()

    print(f"\n  Clean records ready for analysis: {len(df_clean)}")
    print("\nDone. Outputs written to output/")

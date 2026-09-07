"""
Datetime Feature Engineering Pipeline for Transaction Data.

Parses raw timestamp strings and extracts temporal features
required for grouping, trend analysis, and churn prediction.

Tasks:
  1. Parse timestamp strings with explicit format
  2. Extract day-of-week and hour-of-day
  3. Compute week number and resample to weekly buckets
  4. Compute days-since-last-purchase (recency metric)
  5. Build time-indexed multi-dimensional aggregation
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

random.seed(42)
np.random.seed(42)

# ---------------------------------------------------------------------------
# Synthetic transaction dataset
# ---------------------------------------------------------------------------

CUSTOMERS = [f"C{str(i).zfill(3)}" for i in range(1, 21)]   # C001..C020
PRODUCTS  = ["Electronics", "Clothing", "Home Appliances", "Sports", "Books"]

def _rand_ts(start: datetime, end: datetime) -> str:
    delta = int((end - start).total_seconds())
    t = start + timedelta(seconds=random.randint(0, delta))
    return t.strftime("%Y-%m-%d %H:%M:%S")


def create_transaction_dataset(n: int = 300) -> pd.DataFrame:
    """Generate synthetic transaction records with raw timestamp strings."""
    start = datetime(2024, 1, 1)
    end   = datetime(2025, 3, 31, 23, 59, 59)

    records = []
    for _ in range(n):
        cust = random.choice(CUSTOMERS)
        prod = random.choice(PRODUCTS)
        amt  = round(random.uniform(10, 500), 2)
        ts   = _rand_ts(start, end)
        records.append({"customer_id": cust, "product": prod,
                         "amount": amt, "transaction_date": ts})

    df = pd.DataFrame(records)

    # Inject a handful of deliberately messy rows for edge-case section
    messy = pd.DataFrame([
        {"customer_id": "C021", "product": "Books",
         "amount": 29.99, "transaction_date": "2025-01-15 14:30:45"},
        {"customer_id": "C022", "product": "Clothing",
         "amount": 59.00, "transaction_date": "2025-02-28 09:05:00"},
    ])
    df = pd.concat([df, messy], ignore_index=True)
    return df


# ---------------------------------------------------------------------------
# Task 1 -- Parse timestamp strings with explicit format
# ---------------------------------------------------------------------------

TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"


def parse_timestamps(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert 'transaction_date' from string to datetime64 using explicit format.

    Why explicit format matters:
      pd.to_datetime() without format= tries multiple parsers internally and can
      silently misinterpret ambiguous dates (e.g., '01/02/03' -> wrong year).
      Specifying format= raises immediately on the first non-conforming value,
      making data quality issues visible rather than silent.
    """
    print("\n" + "=" * 60)
    print("TASK 1: PARSE TIMESTAMP STRINGS")
    print("=" * 60)

    print(f"Format string used: '{TIMESTAMP_FORMAT}'")
    print(f"  %Y = 4-digit year   %m = 2-digit month  %d = 2-digit day")
    print(f"  %H = hour (00-23)   %M = minutes        %S = seconds")
    print(f"\nDtype BEFORE parsing: {df['transaction_date'].dtype}")

    sample_before = df["transaction_date"].head(3).tolist()
    print(f"Sample raw strings:  {sample_before}")

    df["transaction_date"] = pd.to_datetime(
        df["transaction_date"],
        format=TIMESTAMP_FORMAT,
    )

    print(f"\nDtype AFTER  parsing: {df['transaction_date'].dtype}")
    print(f"Sample parsed values:")
    print(df["transaction_date"].head(3).to_string())

    assert str(df["transaction_date"].dtype).startswith("datetime64"), \
        "Parsing failed: column is not datetime64"

    print(f"\nDate range in dataset:")
    print(f"  Min: {df['transaction_date'].min()}")
    print(f"  Max: {df['transaction_date'].max()}")
    print(f"  Span: {(df['transaction_date'].max() - df['transaction_date'].min()).days} days")

    return df


# ---------------------------------------------------------------------------
# Task 2 -- Extract day-of-week and hour-of-day
# ---------------------------------------------------------------------------

def extract_day_and_hour(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create temporal features for traffic and engagement pattern analysis.

    .dt accessor is ONLY available after the column is datetime64.
    On a string column it raises AttributeError -- this is why Task 1 must run first.
    """
    print("\n" + "=" * 60)
    print("TASK 2: EXTRACT DAY-OF-WEEK AND HOUR-OF-DAY")
    print("=" * 60)

    df["day_of_week"]  = df["transaction_date"].dt.day_name()
    df["day_num"]      = df["transaction_date"].dt.weekday      # 0=Mon, 6=Sun
    df["hour"]         = df["transaction_date"].dt.hour
    df["month"]        = df["transaction_date"].dt.month
    df["month_name"]   = df["transaction_date"].dt.month_name()
    df["is_weekend"]   = df["day_num"].isin([5, 6]).astype(int)

    print(f"Features extracted via .dt accessor:")
    print(f"  day_of_week  : {df['day_of_week'].unique().tolist()}")
    print(f"  hour         : min={df['hour'].min()}  max={df['hour'].max()}")
    print(f"  month        : {sorted(df['month'].unique().tolist())}")
    print(f"  is_weekend   : {df['is_weekend'].value_counts().to_dict()}")

    print("\nTransaction volume by day of week:")
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    daily_vol = (df.groupby("day_of_week")["amount"]
                   .agg(count="count", total="sum", avg="mean")
                   .reindex(day_order)
                   .dropna())
    print(daily_vol.to_string())

    print("\nTransaction volume by hour (0-23):")
    hourly_vol = df.groupby("hour").size().rename("count")
    print(hourly_vol.to_string())

    peak_hour = hourly_vol.idxmax()
    peak_day  = df.groupby("day_of_week").size().idxmax()
    print(f"\nPeak hour:       {peak_hour}:00")
    print(f"Busiest day:     {peak_day}")

    return df


# ---------------------------------------------------------------------------
# Task 3 -- Compute week number and resample to weekly buckets
# ---------------------------------------------------------------------------

def compute_week_and_resample(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add ISO week numbers and produce weekly revenue/count/avg aggregations.

    .resample() requires a DatetimeIndex.  We temporarily set transaction_date
    as the index, resample, then reset the index for the returned DataFrame.
    """
    print("\n" + "=" * 60)
    print("TASK 3: WEEK NUMBER AND WEEKLY RESAMPLING")
    print("=" * 60)

    # ISO week number (1-53)
    df["week_num"] = df["transaction_date"].dt.isocalendar().week.astype(int)
    df["year"]     = df["transaction_date"].dt.year

    print(f"Weeks in dataset: {df['week_num'].nunique()}")
    print(f"Sample week_num values: {df['week_num'].head(6).tolist()}")

    # Sort chronologically before resampling
    df_sorted = df.sort_values("transaction_date")
    df_ts     = df_sorted.set_index("transaction_date")

    # 'W' = week ending Sunday; 'W-MON' for week ending Monday
    weekly = df_ts["amount"].resample("W").agg(
        weekly_revenue="sum",
        transaction_count="count",
        avg_transaction="mean",
    ).round(2)

    print(f"\nWeekly revenue / count / avg (first 10 weeks):")
    print(weekly.head(10).to_string())

    print(f"\nWeekly summary stats:")
    print(f"  Total weeks with data:  {(weekly['transaction_count'] > 0).sum()}")
    print(f"  Peak revenue week:      {weekly['weekly_revenue'].idxmax().date()}  "
          f"(${weekly['weekly_revenue'].max():,.2f})")
    print(f"  Highest volume week:    {weekly['transaction_count'].idxmax().date()}  "
          f"({weekly['transaction_count'].max()} txns)")

    # Store weekly metrics for later reference
    os.makedirs("output", exist_ok=True)
    weekly.to_csv("output/weekly_revenue.csv")
    print("  Weekly metrics saved to output/weekly_revenue.csv")

    return df


# ---------------------------------------------------------------------------
# Task 4 -- Compute days-since-last-purchase (recency)
# ---------------------------------------------------------------------------

def compute_recency(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build recency features for customer churn prediction.

    Recency = days since a customer last transacted.
    Customers with high recency (many days) are at churn risk.

    Datetime arithmetic:
        (reference_date - purchase_date) returns a Timedelta Series
        .dt.days extracts the integer day count from each Timedelta
    """
    print("\n" + "=" * 60)
    print("TASK 4: DAYS-SINCE-LAST-PURCHASE (RECENCY)")
    print("=" * 60)

    # Use a fixed reference date so the script is reproducible
    reference_date = pd.Timestamp("2025-04-01")
    print(f"Reference date (today proxy): {reference_date.date()}")

    # Last purchase date per customer
    customer_last = (df.groupby("customer_id")["transaction_date"]
                       .max()
                       .rename("last_purchase_date"))

    recency = (reference_date - customer_last).dt.days.rename("days_since_last_purchase")

    recency_df = pd.concat([customer_last, recency], axis=1).sort_values(
        "days_since_last_purchase"
    )

    print(f"\nRecency distribution (days since last purchase):")
    print(recency_df["days_since_last_purchase"].describe().round(1).to_string())

    print(f"\nMost recent customers (lowest recency):")
    print(recency_df.head(5).to_string())

    print(f"\nCustomers at churn risk (recency > 90 days):")
    at_risk = recency_df[recency_df["days_since_last_purchase"] > 90]
    print(f"  Count: {len(at_risk)} out of {len(recency_df)} customers")
    if not at_risk.empty:
        print(at_risk.to_string())

    # Merge recency back into main DataFrame
    df = df.merge(recency_df[["days_since_last_purchase"]],
                  on="customer_id", how="left")

    # Segment by recency bucket
    def recency_segment(days):
        if days <= 30:
            return "Active (<=30 days)"
        elif days <= 90:
            return "At-risk (31-90 days)"
        else:
            return "Churned (>90 days)"

    df["recency_segment"] = df["days_since_last_purchase"].apply(recency_segment)

    print(f"\nRecency segment distribution:")
    print(df.drop_duplicates("customer_id")["recency_segment"].value_counts().to_string())

    return df


# ---------------------------------------------------------------------------
# Task 5 -- Time-indexed multi-dimensional aggregation
# ---------------------------------------------------------------------------

def build_time_aggregations(df: pd.DataFrame) -> pd.DataFrame:
    """
    Group by day-of-week x hour to identify peak activity windows.

    Produces:
      - Multi-level groupby: day_of_week x hour -> sum / count / mean
      - Pivot table: hour (rows) x day_of_week (cols) -> sum of amount
      - Peak 3-hour window identification
    """
    print("\n" + "=" * 60)
    print("TASK 5: TIME-INDEXED MULTI-DIMENSIONAL AGGREGATION")
    print("=" * 60)

    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday",
                 "Friday", "Saturday", "Sunday"]

    # Multi-level groupby: 3 aggregation functions
    print("\nGroupby day_of_week x hour -- sum / count / mean:")
    hourly_daily = (df.groupby(["day_of_week", "hour"])
                      .agg(total_amount=("amount", "sum"),
                           transaction_count=("amount", "count"),
                           avg_amount=("amount", "mean"))
                      .round(2))
    print(hourly_daily.head(14).to_string())

    # Pivot table: hour (rows) x day (columns) -> revenue heat map
    print("\nPivot table: Hour x Day-of-Week (total revenue $):")
    pivot = pd.pivot_table(
        df,
        values="amount",
        index="hour",
        columns="day_of_week",
        aggfunc="sum",
        fill_value=0,
    )
    # Reorder columns to Mon-Sun
    pivot = pivot.reindex(columns=[d for d in day_order if d in pivot.columns])
    print(pivot.to_string())

    # Identify top 5 peak hour-day combinations
    print("\nTop 5 peak activity windows (hour x day):")
    peak_df = (df.groupby(["day_of_week", "hour"])
                 .agg(total=("amount", "sum"), count=("amount", "count"))
                 .reset_index()
                 .sort_values("total", ascending=False)
                 .head(5))
    print(peak_df.to_string(index=False))

    # Weekly trend by product category
    print("\nWeekly revenue by product (week_num):")
    product_weekly = (df.groupby(["week_num", "product"])["amount"]
                        .sum()
                        .unstack(fill_value=0)
                        .round(2))
    print(product_weekly.head(8).to_string())

    # Save pivot to output
    pivot.to_csv("output/hour_day_pivot.csv")
    print("\nPivot table saved to output/hour_day_pivot.csv")

    return df


# ---------------------------------------------------------------------------
# Edge-case tests: format validation
# ---------------------------------------------------------------------------

def run_format_edge_cases():
    """
    Demonstrate which timestamp formats parse with the strict explicit format
    and which correctly raise an error.
    """
    print("\n" + "=" * 60)
    print("EDGE CASES: FORMAT VALIDATION")
    print("=" * 60)

    test_dates = [
        ("2025-01-15 14:30:45",   True,  "Standard -- expected to pass"),
        ("2025-1-15 14:30:45",    True,  "Single-digit month -- pandas %m is flexible (note for video)"),
        ("15/01/2025 14:30:45",   False, "European format DD/MM/YYYY -- format mismatch"),
        ("2025-01-15T14:30:45Z",  False, "ISO 8601 with T and Z -- format mismatch"),
        ("2025-02-28 09:05:00",   True,  "Feb 28 -- should parse fine"),
    ]

    print(f"Testing against explicit format: '{TIMESTAMP_FORMAT}'\n")
    for date_str, should_pass, note in test_dates:
        try:
            result = pd.to_datetime(date_str, format=TIMESTAMP_FORMAT)
            status = "PASS" if should_pass else "UNEXPECTED PASS"
            print(f"  [{status}]  {repr(date_str):35s}  -> {result}  ({note})")
        except Exception as e:
            status = "FAIL (expected)" if not should_pass else "UNEXPECTED FAIL"
            print(f"  [{status}]  {repr(date_str):35s}  -> {type(e).__name__}  ({note})")


# ---------------------------------------------------------------------------
# Pipeline summary
# ---------------------------------------------------------------------------

def print_pipeline_summary(df: pd.DataFrame, df_raw: pd.DataFrame):
    print("\n" + "=" * 60)
    print("PIPELINE SUMMARY")
    print("=" * 60)

    print(f"Rows processed:          {len(df)}")
    print(f"Customers:               {df['customer_id'].nunique()}")
    print(f"Date range:              {df['transaction_date'].min().date()} to "
          f"{df['transaction_date'].max().date()}")
    print(f"Days in dataset:         "
          f"{(df['transaction_date'].max() - df['transaction_date'].min()).days}")
    print(f"Unique hours with data:  {sorted(df['hour'].unique().tolist())}")
    print(f"Weeks in dataset:        {df['week_num'].nunique()}")
    print(f"Days-since (min/max):    {df['days_since_last_purchase'].min()} / "
          f"{df['days_since_last_purchase'].max()}")

    new_cols = [c for c in df.columns if c not in df_raw.columns]
    print(f"\nNew features engineered: {len(new_cols)}")
    for c in new_cols:
        print(f"  + {c}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("DATETIME FEATURE ENGINEERING PIPELINE")
    print("Customer Transaction Analysis")
    print("=" * 60)

    # Create dataset
    df_raw = create_transaction_dataset(n=300)
    df = df_raw.copy()

    print(f"\nDataset: {len(df)} rows x {len(df.columns)} columns")
    print(f"Columns: {list(df.columns)}")
    print(f"\nRaw sample (first 5 rows):")
    print(df.head(5).to_string())
    print(f"\ntransaction_date dtype (raw): {df['transaction_date'].dtype}  <-- string, not datetime")

    # Task 1
    df = parse_timestamps(df)

    # Task 2
    df = extract_day_and_hour(df)

    # Task 3
    df = compute_week_and_resample(df)

    # Task 4
    df = compute_recency(df)

    # Task 5
    df = build_time_aggregations(df)

    # Edge cases
    run_format_edge_cases()

    # Summary
    print_pipeline_summary(df, df_raw)

    # Persist cleaned data
    os.makedirs("output", exist_ok=True)
    df.to_csv("output/transactions_with_datetime_features.csv", index=False)
    print("\nEnriched dataset saved to output/transactions_with_datetime_features.csv")

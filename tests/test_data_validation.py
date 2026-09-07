"""
Unit tests for Assignment 24: Data Validation Rules Pipeline.

Covers all 5 task categories:
  Task 1 - Range checks (age, price, birth_date)
  Task 2 - Null constraints (customer_id, email)
  Task 3 - Format pattern validation (email, phone)
  Task 4 - Business rule validation (campaign date order)
  Task 5 - Validation report (passes_all_checks, failures CSV, report dict)
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path

from scripts.data_validation import (
    create_campaign_dataset,
    apply_range_checks,
    apply_null_constraints,
    apply_format_checks,
    apply_business_rules,
    build_validation_report,
    VALIDATION_COLS,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def clean_df():
    """A fully valid record set — every rule should pass."""
    return pd.DataFrame({
        "customer_id":    ["C001", "C002", "C003"],
        "age":            [25, 40, 65],
        "price":          [100.0, 250.0, 50.0],
        "birth_date":     pd.to_datetime(["1990-05-10", "1975-03-22", "1955-11-01"]),
        "campaign_start": pd.to_datetime(["2024-01-01", "2024-03-01", "2024-06-01"]),
        "campaign_end":   pd.to_datetime(["2024-02-01", "2024-04-01", "2024-07-01"]),
        "email":          ["a@b.com", "x@y.org", "m@n.net"],
        "phone":          ["1234567890", "9876543210", "5550001111"],
    })


@pytest.fixture
def dirty_df():
    """Records with one violation of each rule category."""
    return pd.DataFrame({
        "customer_id":    [np.nan, "C002", "C003", "C004", "C005", "C006", "C007"],
        "age":            [25, 200, 30, 45, 50, 60, 70],
        "price":          [100.0, 50.0, -10.0, 200.0, 75.0, 300.0, 150.0],
        "birth_date":     pd.to_datetime([
            "1990-01-01",
            "1980-01-01",
            "1975-01-01",
            "2050-01-01",   # future birth date
            "1960-01-01",
            "1985-01-01",
            "1970-01-01",
        ]),
        "campaign_start": pd.to_datetime([
            "2024-01-01", "2024-02-01", "2024-03-01",
            "2024-04-01", "2024-05-01", "2024-06-01", "2024-07-01",
        ]),
        "campaign_end":   pd.to_datetime([
            "2024-02-01", "2024-03-01", "2024-04-01",
            "2024-05-01", "2024-03-01",  # end before start
            "2024-07-01", "2024-08-01",
        ]),
        "email":          [
            "a@b.com", "x@y.org", "m@n.net",
            "m@n.net", "user_no_at_sign.com",  # missing @
            "p@q.com", "r@s.com",
        ],
        "phone":          [
            "1234567890", "9876543210", "5550001111",
            "5550001111", "5550001111",
            "ABC123",       # invalid phone
            "9991112222",
        ],
    })


# ---------------------------------------------------------------------------
# Task 1 — Range Checks
# ---------------------------------------------------------------------------

class TestRangeChecks:
    def test_valid_age_passes(self, clean_df):
        df = apply_range_checks(clean_df)
        assert df["valid_age"].all()

    def test_invalid_age_fails(self, dirty_df):
        df = apply_range_checks(dirty_df)
        assert not df.loc[1, "valid_age"]   # age = 200

    def test_valid_price_passes(self, clean_df):
        df = apply_range_checks(clean_df)
        assert df["valid_price"].all()

    def test_negative_price_fails(self, dirty_df):
        df = apply_range_checks(dirty_df)
        assert not df.loc[2, "valid_price"]  # price = -10

    def test_valid_birth_date_passes(self, clean_df):
        df = apply_range_checks(clean_df)
        assert df["valid_birth_date"].all()

    def test_future_birth_date_fails(self, dirty_df):
        df = apply_range_checks(dirty_df)
        assert not df.loc[3, "valid_birth_date"]   # 2050-01-01

    def test_columns_created(self, clean_df):
        df = apply_range_checks(clean_df)
        for col in ["valid_age", "valid_price", "valid_birth_date"]:
            assert col in df.columns


# ---------------------------------------------------------------------------
# Task 2 — Null Constraints
# ---------------------------------------------------------------------------

class TestNullConstraints:
    def test_valid_customer_id_passes(self, clean_df):
        df = apply_null_constraints(clean_df)
        assert df["valid_customer_id"].all()

    def test_null_customer_id_fails(self, dirty_df):
        df = apply_null_constraints(dirty_df)
        assert not df.loc[0, "valid_customer_id"]   # NaN customer_id

    def test_valid_email_null_passes(self, clean_df):
        df = apply_null_constraints(clean_df)
        assert df["valid_email_null"].all()

    def test_columns_created(self, clean_df):
        df = apply_null_constraints(clean_df)
        for col in ["valid_customer_id", "valid_email_null"]:
            assert col in df.columns


# ---------------------------------------------------------------------------
# Task 3 — Format Pattern Validation
# ---------------------------------------------------------------------------

class TestFormatChecks:
    def test_valid_email_format_passes(self, clean_df):
        df = apply_format_checks(clean_df)
        assert df["valid_email_format"].all()

    def test_missing_at_sign_fails(self, dirty_df):
        df = apply_format_checks(dirty_df)
        assert not df.loc[4, "valid_email_format"]  # "user_no_at_sign.com"

    def test_valid_phone_passes(self, clean_df):
        df = apply_format_checks(clean_df)
        assert df["valid_phone"].all()

    def test_invalid_phone_fails(self, dirty_df):
        df = apply_format_checks(dirty_df)
        assert not df.loc[5, "valid_phone"]         # "ABC123"

    def test_columns_created(self, clean_df):
        df = apply_format_checks(clean_df)
        for col in ["valid_email_format", "valid_phone"]:
            assert col in df.columns


# ---------------------------------------------------------------------------
# Task 4 — Business Rule Validation
# ---------------------------------------------------------------------------

class TestBusinessRules:
    def test_valid_date_order_passes(self, clean_df):
        df = apply_business_rules(clean_df)
        assert df["valid_date_order"].all()

    def test_end_before_start_fails(self, dirty_df):
        df = apply_business_rules(dirty_df)
        assert not df.loc[4, "valid_date_order"]    # end (2024-03-01) < start (2024-05-01)

    def test_equal_dates_pass(self):
        df = pd.DataFrame({
            "campaign_start": pd.to_datetime(["2024-01-01"]),
            "campaign_end":   pd.to_datetime(["2024-01-01"]),
        })
        df = apply_business_rules(df)
        assert df.loc[0, "valid_date_order"]

    def test_column_created(self, clean_df):
        df = apply_business_rules(clean_df)
        assert "valid_date_order" in df.columns


# ---------------------------------------------------------------------------
# Task 5 — Validation Report
# ---------------------------------------------------------------------------

class TestValidationReport:
    def _prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        df = apply_range_checks(df)
        df = apply_null_constraints(df)
        df = apply_format_checks(df)
        df = apply_business_rules(df)
        return df

    def test_all_pass_on_clean_data(self, clean_df, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "output").mkdir()
        df = self._prepare(clean_df)
        df, failures, report = build_validation_report(df)
        assert report["failed"] == 0
        assert report["passed"] == len(clean_df)

    def test_failures_isolated(self, dirty_df, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "output").mkdir()
        df = self._prepare(dirty_df)
        df, failures, report = build_validation_report(df)
        assert len(failures) == report["failed"]
        assert report["failed"] > 0

    def test_passes_all_checks_column_created(self, clean_df, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "output").mkdir()
        df = self._prepare(clean_df)
        df, _, _ = build_validation_report(df)
        assert "passes_all_checks" in df.columns

    def test_validation_failures_csv_written(self, dirty_df, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "output").mkdir()
        df = self._prepare(dirty_df)
        build_validation_report(df)
        assert (tmp_path / "output" / "validation_failures.csv").exists()

    def test_report_structure(self, dirty_df, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "output").mkdir()
        df = self._prepare(dirty_df)
        _, _, report = build_validation_report(df)
        for key in ["total_records", "passed", "failed", "pass_rate_pct", "rules"]:
            assert key in report

    def test_pass_plus_fail_equals_total(self, dirty_df, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "output").mkdir()
        df = self._prepare(dirty_df)
        _, _, report = build_validation_report(df)
        assert report["passed"] + report["failed"] == report["total_records"]

    def test_rule_keys_in_report(self, clean_df, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "output").mkdir()
        df = self._prepare(clean_df)
        _, _, report = build_validation_report(df)
        expected_rules = {col.replace("valid_", "") for col in VALIDATION_COLS}
        assert expected_rules == set(report["rules"].keys())

    def test_clean_subset_has_no_failures(self, dirty_df, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "output").mkdir()
        df = self._prepare(dirty_df)
        df, _, _ = build_validation_report(df)
        df_clean = df[df["passes_all_checks"]]
        assert df_clean[VALIDATION_COLS].all(axis=None)


# ---------------------------------------------------------------------------
# Dataset generation sanity check
# ---------------------------------------------------------------------------

class TestDatasetCreation:
    def test_creates_expected_rows(self):
        df = create_campaign_dataset(n=150)
        assert len(df) == 150

    def test_has_required_columns(self):
        df = create_campaign_dataset(n=150)
        required = ["customer_id", "age", "price", "birth_date",
                    "campaign_start", "campaign_end", "email", "phone"]
        for col in required:
            assert col in df.columns

    def test_injected_future_birth_dates(self):
        df = create_campaign_dataset(n=150)
        future = df["birth_date"] > pd.Timestamp.now()
        assert future.sum() >= 5

    def test_injected_negative_prices(self):
        df = create_campaign_dataset(n=150)
        assert (df["price"] < 0).sum() >= 4

    def test_injected_null_customer_ids(self):
        df = create_campaign_dataset(n=150)
        assert df["customer_id"].isna().sum() >= 6

    def test_injected_invalid_date_orders(self):
        df = create_campaign_dataset(n=150)
        assert (df["campaign_end"] < df["campaign_start"]).sum() >= 5

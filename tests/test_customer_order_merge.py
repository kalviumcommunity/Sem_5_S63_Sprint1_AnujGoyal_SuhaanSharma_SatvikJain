"""
Unit tests for Assignment 25: Customer-Order Merge & Join Validation Pipeline.

Covers all 5 task categories:
  Task 1 - Explicit join with row count validation
  Task 2 - Unmatched key detection
  Task 3 - Join type comparison
  Task 4 - Merge integrity validation
  Task 5 - Join decision report structure
"""

import json
import pytest
import pandas as pd
import numpy as np

from scripts.customer_order_merge import (
    create_customers,
    create_orders,
    task1_join_with_row_count,
    task2_detect_unmatched_keys,
    task3_compare_join_types,
    task4_validate_merge_integrity,
    task5_join_decision_report,
)


# ---------------------------------------------------------------------------
# Fixtures — small deterministic tables for fast unit tests
# ---------------------------------------------------------------------------

@pytest.fixture
def df_customers():
    """5 customers; C003 and C004 will have no matching orders."""
    return pd.DataFrame({
        "customer_id": ["C001", "C002", "C003", "C004", "C005"],
        "name":        ["Alice", "Bob", "Carol", "Dan", "Eve"],
        "region":      ["North", "South", "East", "West", "North"],
        "segment":     ["Retail", "B2B", "SMB", "Retail", "B2B"],
        "signup_year": [2020, 2021, 2022, 2023, 2024],
    })


@pytest.fixture
def df_orders():
    """
    8 orders across C001, C002, C005 only.
    ORD006/ORD007/ORD008 reference C999 (orphaned — not in customers table).
    """
    return pd.DataFrame({
        "order_id":    ["ORD001", "ORD002", "ORD003", "ORD004",
                        "ORD005", "ORD006", "ORD007", "ORD008"],
        "customer_id": ["C001", "C001", "C002", "C002",
                        "C005", "C999", "C999", "C999"],
        "amount":      [100.0, 200.0, 150.0, 300.0, 250.0, 50.0, 75.0, 90.0],
        "status":      ["Completed", "Pending", "Completed", "Cancelled",
                        "Completed", "Pending", "Pending", "Pending"],
        "order_year":  [2023, 2024, 2023, 2024, 2024, 2023, 2024, 2024],
        "order_month": [1, 3, 6, 9, 2, 4, 7, 11],
    })


# ---------------------------------------------------------------------------
# Task 1 — Explicit join with row count validation
# ---------------------------------------------------------------------------

class TestTask1JoinWithRowCount:
    def test_left_join_returns_dataframe(self, df_customers, df_orders):
        result = task1_join_with_row_count(df_customers, df_orders)
        assert isinstance(result, pd.DataFrame)

    def test_result_has_all_customer_keys(self, df_customers, df_orders):
        result = task1_join_with_row_count(df_customers, df_orders)
        assert set(df_customers["customer_id"]).issubset(set(result["customer_id"]))

    def test_row_count_expands_with_multiple_orders(self, df_customers, df_orders):
        """C001 has 2 orders and C002 has 2 orders → result > customers."""
        result = task1_join_with_row_count(df_customers, df_orders)
        assert len(result) > len(df_customers)

    def test_result_contains_customer_and_order_columns(self, df_customers, df_orders):
        result = task1_join_with_row_count(df_customers, df_orders)
        for col in ["customer_id", "name", "order_id", "amount"]:
            assert col in result.columns

    def test_no_column_conflicts(self, df_customers, df_orders):
        """No _x/_y suffixes should appear — join key is shared, rest are unique."""
        result = task1_join_with_row_count(df_customers, df_orders)
        conflict_cols = [c for c in result.columns if c.endswith("_x") or c.endswith("_y")]
        assert conflict_cols == []

    def test_expected_row_count(self, df_customers, df_orders):
        """
        5 customers × left join with 8 orders:
        C001→2, C002→2, C003→0(NaN row), C004→0(NaN row), C005→1, plus C999 excluded.
        Expected = 2+2+1+1+1 = 7 rows.
        """
        result = task1_join_with_row_count(df_customers, df_orders)
        assert len(result) == 7


# ---------------------------------------------------------------------------
# Task 2 — Detect unmatched keys
# ---------------------------------------------------------------------------

class TestTask2UnmatchedKeys:
    def test_returns_two_dataframes(self, df_customers, df_orders):
        uc, uo = task2_detect_unmatched_keys(df_customers, df_orders)
        assert isinstance(uc, pd.DataFrame)
        assert isinstance(uo, pd.DataFrame)

    def test_correct_count_unmatched_customers(self, df_customers, df_orders):
        """C003 and C004 have no orders."""
        uc, _ = task2_detect_unmatched_keys(df_customers, df_orders)
        assert len(uc) == 2
        assert set(uc["customer_id"]) == {"C003", "C004"}

    def test_correct_count_orphaned_orders(self, df_customers, df_orders):
        """ORD006/007/008 reference C999 which isn't in customers."""
        _, uo = task2_detect_unmatched_keys(df_customers, df_orders)
        assert len(uo) == 3
        assert (uo["customer_id"] == "C999").all()

    def test_csv_files_written(self, df_customers, df_orders, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "output").mkdir()
        task2_detect_unmatched_keys(df_customers, df_orders)
        assert (tmp_path / "output" / "unmatched_customers.csv").exists()
        assert (tmp_path / "output" / "unmatched_orders.csv").exists()

    def test_no_overlap_between_unmatched_sets(self, df_customers, df_orders):
        """Unmatched customers are in df_customers; orphaned orders are NOT."""
        uc, uo = task2_detect_unmatched_keys(df_customers, df_orders)
        uc_ids = set(uc["customer_id"])
        customer_ids = set(df_customers["customer_id"])
        assert uc_ids.issubset(customer_ids)
        assert not set(uo["customer_id"]).intersection(customer_ids)


# ---------------------------------------------------------------------------
# Task 3 — Compare join types
# ---------------------------------------------------------------------------

class TestTask3JoinTypeComparison:
    def test_returns_dict_with_four_keys(self, df_customers, df_orders):
        result = task3_compare_join_types(df_customers, df_orders)
        assert set(result.keys()) == {"inner", "left", "right", "outer"}

    def test_inner_le_left_le_outer(self, df_customers, df_orders):
        """Row count ordering: inner ≤ left ≤ outer."""
        r = task3_compare_join_types(df_customers, df_orders)
        assert r["inner"] <= r["left"] <= r["outer"]

    def test_inner_le_right_le_outer(self, df_customers, df_orders):
        r = task3_compare_join_types(df_customers, df_orders)
        assert r["inner"] <= r["right"] <= r["outer"]

    def test_inner_loses_unmatched_customers(self, df_customers, df_orders):
        """Inner join < left join by the number of unmatched customer rows."""
        r = task3_compare_join_types(df_customers, df_orders)
        uc, _ = task2_detect_unmatched_keys(df_customers, df_orders)
        assert r["left"] - r["inner"] == len(uc)

    def test_outer_includes_both_orphan_groups(self, df_customers, df_orders):
        """Outer join must be >= right join (adds unmatched customers back)."""
        r = task3_compare_join_types(df_customers, df_orders)
        assert r["outer"] >= r["right"]

    def test_right_vs_inner_equals_orphaned_orders(self, df_customers, df_orders):
        """Right join adds orphaned-order rows that inner drops."""
        r = task3_compare_join_types(df_customers, df_orders)
        _, uo = task2_detect_unmatched_keys(df_customers, df_orders)
        assert r["right"] - r["inner"] == len(uo)


# ---------------------------------------------------------------------------
# Task 4 — Merge integrity validation
# ---------------------------------------------------------------------------

class TestTask4MergeIntegrity:
    def _merged(self, df_customers, df_orders):
        return task1_join_with_row_count(df_customers, df_orders)

    def test_returns_dict_with_expected_keys(self, df_customers, df_orders):
        stats = task4_validate_merge_integrity(self._merged(df_customers, df_orders))
        for key in [
            "conflict_columns", "max_orders_per_customer",
            "avg_orders_per_customer", "customers_no_orders", "duplicate_order_rows",
        ]:
            assert key in stats

    def test_no_column_conflicts(self, df_customers, df_orders):
        stats = task4_validate_merge_integrity(self._merged(df_customers, df_orders))
        assert stats["conflict_columns"] == []

    def test_max_orders_per_customer_correct(self, df_customers, df_orders):
        """C001 and C002 each have 2 orders → max = 2."""
        stats = task4_validate_merge_integrity(self._merged(df_customers, df_orders))
        assert stats["max_orders_per_customer"] == 2

    def test_customers_no_orders_correct(self, df_customers, df_orders):
        """C003 and C004 have NaN order_id after left join → 2 rows."""
        stats = task4_validate_merge_integrity(self._merged(df_customers, df_orders))
        assert stats["customers_no_orders"] == 2

    def test_no_duplicate_order_rows(self, df_customers, df_orders):
        """Each order_id should appear exactly once in the merged result."""
        stats = task4_validate_merge_integrity(self._merged(df_customers, df_orders))
        assert stats["duplicate_order_rows"] == 0


# ---------------------------------------------------------------------------
# Task 5 — Join decision report
# ---------------------------------------------------------------------------

class TestTask5JoinDecisionReport:
    def _run_all(self, df_customers, df_orders, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "output").mkdir()
        df_merged = task1_join_with_row_count(df_customers, df_orders)
        uc, uo = task2_detect_unmatched_keys(df_customers, df_orders)
        jt = task3_compare_join_types(df_customers, df_orders)
        stats = task4_validate_merge_integrity(df_merged)
        report = task5_join_decision_report(
            df_customers, df_orders, df_merged, uc, uo, jt, stats
        )
        return report, tmp_path

    def test_report_is_dict(self, df_customers, df_orders, tmp_path, monkeypatch):
        report, _ = self._run_all(df_customers, df_orders, tmp_path, monkeypatch)
        assert isinstance(report, dict)

    def test_required_keys_present(self, df_customers, df_orders, tmp_path, monkeypatch):
        report, _ = self._run_all(df_customers, df_orders, tmp_path, monkeypatch)
        for key in [
            "join_type", "left_table", "right_table", "join_key",
            "left_rows", "right_rows", "result_rows",
            "unmatched_left", "unmatched_right",
            "join_type_comparison", "reasoning",
        ]:
            assert key in report, f"Missing key: {key}"

    def test_join_type_is_left(self, df_customers, df_orders, tmp_path, monkeypatch):
        report, _ = self._run_all(df_customers, df_orders, tmp_path, monkeypatch)
        assert report["join_type"] == "left"

    def test_join_key_is_customer_id(self, df_customers, df_orders, tmp_path, monkeypatch):
        report, _ = self._run_all(df_customers, df_orders, tmp_path, monkeypatch)
        assert report["join_key"] == "customer_id"

    def test_row_counts_accurate(self, df_customers, df_orders, tmp_path, monkeypatch):
        report, _ = self._run_all(df_customers, df_orders, tmp_path, monkeypatch)
        assert report["left_rows"] == len(df_customers)
        assert report["right_rows"] == len(df_orders)

    def test_unmatched_counts_accurate(self, df_customers, df_orders, tmp_path, monkeypatch):
        report, _ = self._run_all(df_customers, df_orders, tmp_path, monkeypatch)
        assert report["unmatched_left"] == 2   # C003, C004
        assert report["unmatched_right"] == 3  # C999 orders

    def test_json_file_written(self, df_customers, df_orders, tmp_path, monkeypatch):
        _, tmp_path = self._run_all(df_customers, df_orders, tmp_path, monkeypatch)
        report_path = tmp_path / "output" / "join_decision_report.json"
        assert report_path.exists()
        with open(report_path) as f:
            data = json.load(f)
        assert data["join_type"] == "left"

    def test_reasoning_is_non_empty_string(self, df_customers, df_orders, tmp_path, monkeypatch):
        report, _ = self._run_all(df_customers, df_orders, tmp_path, monkeypatch)
        assert isinstance(report["reasoning"], str)
        assert len(report["reasoning"]) > 50


# ---------------------------------------------------------------------------
# Dataset generation sanity checks
# ---------------------------------------------------------------------------

class TestDatasetGeneration:
    def test_customers_row_count(self):
        df = create_customers(n=1000)
        assert len(df) == 1000

    def test_customers_unique_ids(self):
        df = create_customers(n=1000)
        assert df["customer_id"].nunique() == 1000

    def test_orders_row_count(self):
        df = create_orders(n_orders=5000)
        assert len(df) == 5000

    def test_orders_has_orphans(self):
        """200 orders should reference C9001-C9200 (not in customers table)."""
        df = create_orders(n_orders=5000, n_active_customers=800)
        orphan_mask = df["customer_id"].str.startswith("C9")
        assert orphan_mask.sum() == 200

    def test_customers_required_columns(self):
        df = create_customers(n=100)
        for col in ["customer_id", "name", "region", "segment", "signup_year"]:
            assert col in df.columns

    def test_orders_required_columns(self):
        df = create_orders(n_orders=5000)
        for col in ["order_id", "customer_id", "amount", "status", "order_year", "order_month"]:
            assert col in df.columns

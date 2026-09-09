"""
Concept #34: SQL-Based Insight Validation.

Automated validation script comparing SQL business metrics against equivalent Pandas calculations.

Metrics Compared:
  1. Total Students
  2. Completion Rate (%)
  3. Dropout Rate (%)
  4. Active Learner Count
  5. Average Quiz Score (%)
  6. Average Session Duration (Minutes)
  7. At-Risk Learner Count
"""

import json
import os
import sys
from pathlib import Path

# Ensure project root directory is in Python path for standalone script execution
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
from src.utils import DB_PATH, ensure_directories_exist
from src.database import (
    init_database,
    load_processed_data_to_sqlite,
    validate_sql_insights_against_pandas,
)
from scripts.sql_integration import prepare_project_datasets


def main() -> None:
    print("=" * 75)
    print("CONCEPT #34: SQL-BASED INSIGHT VALIDATION AGAINST PANDAS")
    print("=" * 75)

    ensure_directories_exist()
    target_db = DB_PATH
    print(f"Target Database File: {target_db}")

    # Step 1: Initialize Database & Populate Datasets
    print("\n[Step 1] Initializing database and preparing analytical datasets...")
    init_database(db_path=target_db)
    datasets = prepare_project_datasets()
    load_processed_data_to_sqlite(datasets, db_path=target_db)
    print("  [OK] Database populated successfully.")

    # Step 2: Run Automated SQL vs Pandas Validation
    print("\n[Step 2] Executing SQL vs Pandas metric comparison...")
    report = validate_sql_insights_against_pandas(db_path=target_db, datasets=datasets)

    # Step 3: Format & Display Comparison Results Table
    print("\n" + "=" * 75)
    print(f"{'METRIC NAME':<30} | {'SQL VALUE':<12} | {'PANDAS VALUE':<12} | {'MATCH':<8}")
    print("-" * 75)

    comp_dict = report.get("comparison_results", {})
    records = []
    for metric, res in comp_dict.items():
        sql_v = res["sql_value"]
        pd_v = res["pandas_value"]
        match_str = "PASS" if res["match"] else "FAIL"
        print(f"{metric:<30} | {str(sql_v):<12} | {str(pd_v):<12} | {match_str:<8}")
        records.append({
            "metric": metric,
            "sql_value": sql_v,
            "pandas_value": pd_v,
            "difference": res["absolute_difference"],
            "match": res["match"]
        })

    print("=" * 75)
    print(f"VALIDATION OVERALL STATUS : {report.get('status', 'UNKNOWN')}")
    print(f"METRICS COMPARED          : {report.get('metrics_compared', 0)}")
    print(f"DISCREPANCIES DETECTED    : {len(report.get('discrepancies', []))}")
    print("=" * 75)

    # Step 4: Export Summary JSON Report
    os.makedirs("output", exist_ok=True)
    report_path = Path("output/sql_insight_validation_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"\nValidation report saved to: {report_path}")

    if report.get("status") != "VALID":
        print("\n[ERROR] Insight validation failed due to metric discrepancies!")
        sys.exit(1)
    else:
        print("\n[SUCCESS] All SQL insights perfectly match Pandas calculations!")


if __name__ == "__main__":
    main()

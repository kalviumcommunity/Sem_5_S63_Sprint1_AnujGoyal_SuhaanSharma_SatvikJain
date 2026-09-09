"""
Concept #28: SQL Business Metrics Query Design.

Executes core business metric queries from sql/business_metrics.sql against SQLite analytics database.

Metrics Evaluated:
  1. Completion Rate (%)
  2. Dropout Rate (%)
  3. Average Quiz Score (%)
  4. Average Session Duration (Minutes)
  5. Active Learner Count
  6. At-Risk Learner Count
"""

import json
import os
import sys
from pathlib import Path

# Ensure project root directory is in Python path for standalone script execution
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
from src.utils import DB_PATH, SQL_DIR, ensure_directories_exist
from src.database import (
    init_database,
    load_processed_data_to_sqlite,
    execute_business_metrics,
)
from scripts.sql_integration import prepare_project_datasets


def main() -> None:
    print("=" * 70)
    print("CONCEPT #28: SQL BUSINESS METRICS QUERY DESIGN")
    print("=" * 70)

    ensure_directories_exist()
    target_db = DB_PATH
    print(f"Target Database File: {target_db}")

    # Step 1: Initialize Database & Populate Sample/Processed Data
    print("\n[Step 1] Initializing SQLite database and loading datasets...")
    init_database(db_path=target_db)
    datasets = prepare_project_datasets()
    load_processed_data_to_sqlite(datasets, db_path=target_db)
    print("  [OK] Database populated successfully.")

    # Step 2: Execute Core Business Metric SQL Queries
    print("\n[Step 2] Executing SQL queries from sql/business_metrics.sql...")
    metrics_result = execute_business_metrics(db_path=target_db)
    kpis = metrics_result.get("kpis", {})

    # Step 3: Print Executive KPI Summary Cards
    print("\n" + "=" * 70)
    print("EXECUTIVE BUSINESS KPI SUMMARY")
    print("=" * 70)
    print(f"  Total Registered Students  : {kpis.get('total_students', 0)}")
    print(f"  Course Completion Rate     : {kpis.get('completion_rate_pct', 0.0)}%")
    print(f"  Student Dropout Rate       : {kpis.get('dropout_rate_pct', 0.0)}%")
    print(f"  Average Quiz Score         : {kpis.get('avg_quiz_score_pct', 0.0)}%")
    print(f"  Average Session Duration   : {kpis.get('avg_session_duration_minutes', 0.0)} mins")
    print(f"  Active Learner Count       : {kpis.get('active_learner_count', 0)}")
    print(f"  At-Risk Learner Count      : {kpis.get('at_risk_learner_count', 0)}")

    # Step 4: Print Category Breakdown Table
    cat_df = metrics_result.get("category_breakdown", pd.DataFrame())
    if not cat_df.empty:
        print("\n" + "=" * 70)
        print("BUSINESS METRICS BY COURSE CATEGORY")
        print("=" * 70)
        print(cat_df.to_string(index=False))

    # Step 5: Save Summary Report to Output Directory
    os.makedirs("output", exist_ok=True)
    report_path = Path("output/business_metrics_report.json")
    report_data = {
        "database_path": str(target_db),
        "kpi_summary": kpis,
        "category_breakdown": cat_df.to_dict(orient="records") if not cat_df.empty else [],
    }

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)

    print("\n" + "=" * 70)
    print(f"SQL BUSINESS METRICS COMPLETE. Report saved to: {report_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()

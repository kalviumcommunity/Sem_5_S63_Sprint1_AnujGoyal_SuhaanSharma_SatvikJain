"""
Concept #29: SQL Filtering, Grouping & Aggregation.

Executes business analytics SQL queries using WHERE, GROUP BY, HAVING, COUNT, SUM, AVG
from sql/aggregation.sql against the SQLite analytics database.

Analyses Conducted:
  1. Course Performance & Completion Analysis
  2. Learner Segment & Device Engagement Analysis
  3. High Inactivity Risk Learner Identification
  4. Age Demographic Engagement & Study Habits
  5. Quiz Attempt & Failure Rate Aggregation
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
    execute_aggregation_queries,
)
from scripts.sql_integration import prepare_project_datasets


def main() -> None:
    print("=" * 70)
    print("CONCEPT #29: SQL FILTERING, GROUPING & AGGREGATION")
    print("=" * 70)

    ensure_directories_exist()
    target_db = DB_PATH
    print(f"Target Database File: {target_db}")

    # Step 1: Initialize Database & Populate Sample/Processed Data
    print("\n[Step 1] Initializing SQLite database and ensuring tables are populated...")
    init_database(db_path=target_db)
    datasets = prepare_project_datasets()
    load_processed_data_to_sqlite(datasets, db_path=target_db)
    print("  [OK] Database loaded successfully.")

    # Step 2: Execute Aggregation Queries from sql/aggregation.sql
    print("\n[Step 2] Executing SQL queries from sql/aggregation.sql...")
    aggregation_results = execute_aggregation_queries(db_path=target_db)

    # Step 3: Print Analytical Query Tables
    report_dict = {}

    for query_name, df in aggregation_results.items():
        title = query_name.replace("_", " ").upper()
        print("\n" + "=" * 70)
        print(f"QUERY: {title}")
        print("=" * 70)
        if not df.empty:
            print(df.to_string(index=False))
            report_dict[query_name] = df.to_dict(orient="records")
        else:
            print("  [INFO] No records returned for this filter/grouping constraint.")
            report_dict[query_name] = []

    # Step 4: Save Summary Report to Output Directory
    os.makedirs("output", exist_ok=True)
    report_path = Path("output/sql_aggregation_report.json")
    report_data = {
        "database_path": str(target_db),
        "executed_queries": list(aggregation_results.keys()),
        "results": report_dict,
    }

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)

    print("\n" + "=" * 70)
    print(f"SQL AGGREGATION ANALYSIS COMPLETE. Summary saved to: {report_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()

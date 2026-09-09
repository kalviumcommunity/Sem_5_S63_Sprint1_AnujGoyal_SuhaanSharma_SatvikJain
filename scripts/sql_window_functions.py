"""
Concept #31: SQL Window Functions & Ranking Systems.

Executes SQL window function queries using:
  - ROW_NUMBER()
  - RANK() / DENSE_RANK()
  - LAG()
  - LEAD()
  - AVG() OVER()

Use Cases Demonstrated:
  1. Course-Level Learner Performance Rankings & Benchmarks
  2. Previous Session Activity Comparison (LAG)
  3. Sequential Quiz Progression & Next Attempt Delta (LAG & LEAD)
  4. Rolling 3-Session Average Duration & Benchmark (AVG OVER)
  5. Overall Platform Leaderboard & Global Baseline (RANK & DENSE_RANK)
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
    execute_window_function_queries,
)
from scripts.sql_integration import prepare_project_datasets


def main() -> None:
    print("=" * 70)
    print("CONCEPT #31: SQL WINDOW FUNCTIONS & RANKING SYSTEMS")
    print("=" * 70)

    ensure_directories_exist()
    target_db = DB_PATH
    print(f"Target Database File: {target_db}")

    # Step 1: Initialize Database & Populate Datasets
    print("\n[Step 1] Initializing SQLite database and loading datasets...")
    init_database(db_path=target_db)
    datasets = prepare_project_datasets()
    load_processed_data_to_sqlite(datasets, db_path=target_db)
    print("  [OK] Database loaded successfully.")

    # Step 2: Execute Window Function Queries from sql/window_functions.sql
    print("\n[Step 2] Executing SQL window function queries from sql/window_functions.sql...")
    window_results = execute_window_function_queries(db_path=target_db)

    # Step 3: Print Analytical Query Output Tables
    report_dict = {}

    for query_name, df in window_results.items():
        title = query_name.replace("_", " ").upper()
        print("\n" + "=" * 70)
        print(f"WINDOW QUERY: {title}")
        print("=" * 70)
        if not df.empty:
            # Display sample top 10 rows for clean terminal display
            sample_df = df.head(10)
            print(sample_df.to_string(index=False))
            report_dict[query_name] = df.to_dict(orient="records")
        else:
            print("  [INFO] No records returned for this window function query.")
            report_dict[query_name] = []

    # Step 4: Export Summary Report to Output Directory
    os.makedirs("output", exist_ok=True)
    report_path = Path("output/sql_window_functions_report.json")
    report_data = {
        "database_path": str(target_db),
        "executed_queries": list(window_results.keys()),
        "results": report_dict,
    }

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)

    print("\n" + "=" * 70)
    print(f"SQL WINDOW FUNCTIONS ANALYTICS COMPLETE. Report saved to: {report_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()

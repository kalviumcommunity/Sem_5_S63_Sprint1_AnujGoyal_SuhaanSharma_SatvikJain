"""
Concept #30: SQL Joins & Multi-Table Analysis.

Executes multi-table INNER JOIN and LEFT JOIN queries combining:
  - students
  - courses
  - sessions
  - quizzes
  - behavioural_features

Validates that multi-table joins preserve learner granularity (1.00x expansion factor)
without record duplication.
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
    execute_multi_table_joins,
    validate_join_expansion_integrity,
)
from scripts.sql_integration import prepare_project_datasets


def main() -> None:
    print("=" * 70)
    print("CONCEPT #30: SQL JOINS & MULTI-TABLE ANALYSIS")
    print("=" * 70)

    ensure_directories_exist()
    target_db = DB_PATH
    print(f"Target Database File: {target_db}")

    # Step 1: Initialize Database & Populate Datasets
    print("\n[Step 1] Initializing database schema and populating multi-entity tables...")
    init_database(db_path=target_db)
    datasets = prepare_project_datasets()
    load_processed_data_to_sqlite(datasets, db_path=target_db)
    print("  [OK] Database populated with all 5 core tables.")

    # Step 2: Validate Join Integrity & Non-Duplication
    print("\n[Step 2] Validating multi-table join duplication & expansion factor...")
    integrity_report = validate_join_expansion_integrity(db_path=target_db)
    print(f"  Base Students Count  : {integrity_report['base_students_count']}")
    print(f"  Joined Records Count : {integrity_report['joined_records_count']}")
    print(f"  Expansion Factor     : {integrity_report['expansion_factor']:.4f}x")
    print(f"  Join Integrity Status: {integrity_report['join_integrity_status']}")

    # Step 3: Execute Multi-Table Join Queries
    print("\n[Step 3] Executing multi-table INNER and LEFT JOIN queries from sql/multi_table_joins.sql...")
    join_results = execute_multi_table_joins(db_path=target_db)

    report_dict = {}
    for query_name, df in join_results.items():
        title = query_name.replace("_", " ").upper()
        print("\n" + "=" * 70)
        print(f"MULTI-TABLE QUERY: {title}")
        print("=" * 70)
        if not df.empty:
            # Display sample top 10 rows
            sample_df = df.head(10)
            print(sample_df.to_string(index=False))
            report_dict[query_name] = df.to_dict(orient="records")
        else:
            print("  [INFO] No records returned for this multi-table query.")
            report_dict[query_name] = []

    # Step 4: Export Summary Report to Output Directory
    os.makedirs("output", exist_ok=True)
    report_path = Path("output/sql_joins_report.json")
    report_data = {
        "database_path": str(target_db),
        "join_duplication_integrity": integrity_report,
        "executed_queries": list(join_results.keys()),
        "query_results": report_dict,
    }

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)

    print("\n" + "=" * 70)
    print(f"SQL MULTI-TABLE JOIN ANALYSIS COMPLETE. Report saved to: {report_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()

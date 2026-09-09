"""
Concept #27: SQL Environment & Database Integration.

Integrates SQLite into the Learning Behaviour & Course Completion Analytics platform.
Target Database: learning_analytics.db

Steps:
  1. Initialize SQLite database schema from sql/schema.sql.
  2. Create/Prepare datasets for core tables:
     - students
     - courses
     - sessions
     - quizzes
     - behavioural_features
  3. Insert datasets into SQLite database tables.
  4. Perform data insertion validation and check row counts.
  5. Run analytical SQL verification queries.
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
    validate_database_insertion,
    query_to_dataframe,
)
from src.ingestion import load_all_raw_data
from src.features import engineer_behavioral_features


def create_sample_learning_data() -> dict:
    """Generates synthetic learning analytics data for demonstration when raw files are not present."""
    import numpy as np

    rng = np.random.default_rng(42)
    n_students = 50
    n_courses = 4

    courses_df = pd.DataFrame({
        "course_id": [f"C{str(i).zfill(3)}" for i in range(1, n_courses + 1)],
        "course_title": ["Python for Data Science", "SQL Database Analytics", "Machine Learning Fundamentals", "Web Development"],
        "category": ["Data Science", "Database", "AI", "Development"],
        "total_modules": [12, 10, 15, 8],
        "total_quizzes": [6, 5, 8, 4],
        "estimated_duration_hours": [24.0, 18.0, 30.0, 12.0],
        "difficulty_level": ["Beginner", "Intermediate", "Advanced", "Beginner"]
    })

    students_df = pd.DataFrame({
        "student_id": [f"S{str(i).zfill(4)}" for i in range(1, n_students + 1)],
        "registration_date": pd.date_range("2026-01-01", periods=n_students, freq="D").strftime("%Y-%m-%d"),
        "age": rng.integers(18, 45, size=n_students),
        "gender": rng.choice(["Male", "Female", "Other"], size=n_students),
        "education_level": rng.choice(["High School", "Undergraduate", "Postgraduate"], size=n_students),
        "device_type": rng.choice(["Laptop", "Desktop", "Tablet", "Mobile"], size=n_students),
        "target_course_id": rng.choice(courses_df["course_id"], size=n_students),
        "completion_status": rng.choice(["Completed", "In Progress", "Dropped"], size=n_students, p=[0.4, 0.4, 0.2]),
        "completion_date": [None] * n_students
    })

    sessions_df = pd.DataFrame({
        "session_id": [f"SES{str(i).zfill(5)}" for i in range(1, n_students * 3 + 1)],
        "student_id": rng.choice(students_df["student_id"], size=n_students * 3),
        "course_id": rng.choice(courses_df["course_id"], size=n_students * 3),
        "session_start": pd.date_range("2026-02-01", periods=n_students * 3, freq="6h").strftime("%Y-%m-%d %H:%M:%S"),
        "session_end": pd.date_range("2026-02-01 01:00:00", periods=n_students * 3, freq="6h").strftime("%Y-%m-%d %H:%M:%S"),
        "duration_minutes": rng.uniform(15.0, 120.0, size=n_students * 3).round(1),
        "active_minutes": rng.uniform(10.0, 100.0, size=n_students * 3).round(1),
        "idle_minutes": rng.uniform(2.0, 20.0, size=n_students * 3).round(1),
        "video_watched_minutes": rng.uniform(5.0, 60.0, size=n_students * 3).round(1),
        "reading_minutes": rng.uniform(5.0, 40.0, size=n_students * 3).round(1),
        "modules_accessed": rng.integers(1, 5, size=n_students * 3)
    })

    quizzes_df = pd.DataFrame({
        "quiz_attempt_id": [f"QA{str(i).zfill(5)}" for i in range(1, n_students * 2 + 1)],
        "student_id": rng.choice(students_df["student_id"], size=n_students * 2),
        "course_id": rng.choice(courses_df["course_id"], size=n_students * 2),
        "quiz_id": [f"Q{rng.integers(1, 10)}" for _ in range(n_students * 2)],
        "attempt_number": rng.integers(1, 4, size=n_students * 2),
        "attempt_date": pd.date_range("2026-02-05", periods=n_students * 2, freq="12h").strftime("%Y-%m-%d"),
        "score_percentage": rng.uniform(50.0, 100.0, size=n_students * 2).round(1),
        "time_taken_minutes": rng.uniform(10.0, 45.0, size=n_students * 2).round(1),
        "passed": rng.choice([1, 0], size=n_students * 2, p=[0.8, 0.2])
    })

    return {
        "students": students_df,
        "courses": courses_df,
        "sessions": sessions_df,
        "quizzes": quizzes_df
    }


def prepare_project_datasets() -> dict:
    """Loads raw datasets, applies feature engineering, and formats tables for SQLite."""
    raw = load_all_raw_data()
    datasets = {}

    has_raw = any(not df.empty for df in raw.values()) if raw else False

    if has_raw:
        for name in ["students", "courses", "sessions", "quizzes"]:
            if name in raw and not raw[name].empty:
                datasets[name] = raw[name].copy()
    else:
        print("  [INFO] No raw CSV/JSON files found. Generating sample analytics dataset...")
        datasets = create_sample_learning_data()

    # Derive behavioural_features table via Student 360 merge
    if "students" in datasets:
        from src.merging import build_student_360_dataset

        student_360_df, _ = build_student_360_dataset(
            students_df=datasets.get("students"),
            courses_df=datasets.get("courses"),
            sessions_df=datasets.get("sessions"),
            quizzes_df=datasets.get("quizzes"),
        )
        b_features = engineer_behavioral_features(student_360_df=student_360_df)
        datasets["behavioural_features"] = b_features

    return datasets


def main() -> None:
    print("=" * 70)
    print("CONCEPT #27: SQL ENVIRONMENT & DATABASE INTEGRATION")
    print("=" * 70)

    ensure_directories_exist()
    target_db = DB_PATH
    print(f"Target Database File: {target_db}")

    # Step 1: Initialize Database Schema
    print("\n[Step 1] Initializing SQLite database schema from sql/schema.sql...")
    init_database(db_path=target_db)
    print("  [OK] Database schema successfully initialized.")

    # Step 2: Prepare Datasets
    print("\n[Step 2] Preparing processed datasets for database ingestion...")
    datasets = prepare_project_datasets()
    for name, df in datasets.items():
        print(f"  - Dataset '{name}': {len(df)} rows x {len(df.columns)} columns")

    # Step 3: Load into SQLite
    print("\n[Step 3] Loading datasets into SQLite tables...")
    inserted_summary = load_processed_data_to_sqlite(datasets, db_path=target_db)
    for tbl, count in inserted_summary.items():
        print(f"  - Table '{tbl}': {count} records loaded successfully.")

    # Step 4: Validate Data Insertion
    print("\n[Step 4] Validating database table structures and row counts...")
    validation_report = validate_database_insertion(
        db_path=target_db,
        expected_tables=["students", "courses", "sessions", "quizzes", "behavioural_features"]
    )
    print(f"  Validation Status: {validation_report['status']}")
    print(f"  Row Counts: {validation_report['table_row_counts']}")
    if validation_report["errors"]:
        print(f"  Errors: {validation_report['errors']}")

    # Step 5: SQL Query Verification
    print("\n[Step 5] Executing analytical SQL query checks...")

    sample_query = """
    SELECT
        c.category,
        COUNT(s.student_id) AS total_students,
        ROUND(AVG(bf.engagement_score), 2) AS avg_engagement,
        SUM(CASE WHEN s.completion_status = 'Completed' THEN 1 ELSE 0 END) AS completed_count
    FROM students s
    LEFT JOIN courses c ON s.target_course_id = c.course_id
    LEFT JOIN behavioural_features bf ON s.student_id = bf.student_id
    GROUP BY c.category;
    """

    res_df = query_to_dataframe(sample_query, db_path=target_db)
    print("\n  Sample SQL Query Result (Student Engagement by Category):")
    print(res_df.to_string(index=False))

    # Save summary artifact
    os.makedirs("output", exist_ok=True)
    summary_path = Path("output/sql_integration_summary.json")
    summary_data = {
        "database_path": str(target_db),
        "status": validation_report["status"],
        "inserted_records": inserted_summary,
        "validation_report": validation_report,
    }
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2)

    print("\n" + "=" * 70)
    print(f"SQL INTEGRATION COMPLETE. Summary saved to: {summary_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()

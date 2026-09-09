"""
Database Management Module for Learning Analytics.
Handles SQLite database connection, table initialization, and querying.
"""

from pathlib import Path
from typing import Optional
import sqlite3
import pandas as pd
from src.utils import DB_PATH, SQL_DIR, setup_logger, ensure_directories_exist

logger = setup_logger(__name__)


def get_db_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """Returns a connection to the SQLite database."""
    target_path = db_path or DB_PATH
    ensure_directories_exist()
    return sqlite3.connect(str(target_path))


def init_database(schema_path: Optional[Path] = None, db_path: Optional[Path] = None) -> None:
    """Initializes the database schema using schema.sql."""
    schema_file = schema_path or (SQL_DIR / "schema.sql")
    if not schema_file.exists():
        logger.warning(f"Schema file not found at {schema_file}")
        return
    
    with open(schema_file, "r", encoding="utf-8") as f:
        schema_sql = f.read()
        
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.executescript(schema_sql)
        conn.commit()
        logger.info("Database schema initialized successfully.")
    finally:
        conn.close()


def query_to_dataframe(query: str, db_path: Optional[Path] = None) -> pd.DataFrame:
    """Executes a SQL query and returns the results as a pandas DataFrame."""
    conn = get_db_connection(db_path)
    try:
        return pd.read_sql_query(query, conn)
    finally:
        conn.close()


def load_processed_data_to_sqlite(
    datasets: dict,
    db_path: Optional[Path] = None,
    if_exists: str = "replace"
) -> dict:
    """
    Loads a dictionary of processed DataFrames into SQLite tables.

    Args:
        datasets: Dictionary mapping table name -> pd.DataFrame
        db_path: Optional custom path to SQLite database file
        if_exists: Strategy for existing tables ('replace', 'append', 'fail')

    Returns:
        Dictionary mapping table_name -> inserted_row_count
    """
    from src.storage import save_to_database

    target_db = db_path or DB_PATH
    init_database(db_path=target_db)
    inserted_counts = {}

    for table_name, df in datasets.items():
        if df is not None and not df.empty:
            save_to_database(df, table_name, db_path=target_db, if_exists=if_exists)
            inserted_counts[table_name] = len(df)
            logger.info(f"Loaded {len(df)} rows into table '{table_name}'.")

    return inserted_counts


def validate_database_insertion(
    db_path: Optional[Path] = None,
    expected_tables: Optional[list] = None
) -> dict:
    """
    Validates that database tables exist and contain valid inserted data.

    Args:
        db_path: Path to SQLite database
        expected_tables: List of expected table names

    Returns:
        Dictionary containing validation status, table row counts, and error details
    """
    tables_to_check = expected_tables or ["students", "courses", "sessions", "quizzes", "behavioural_features"]
    conn = get_db_connection(db_path)
    report = {
        "status": "VALID",
        "existing_tables": [],
        "missing_tables": [],
        "table_row_counts": {},
        "errors": []
    }

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        db_tables = set(row[0] for row in cursor.fetchall())
        report["existing_tables"] = list(db_tables)

        for table in tables_to_check:
            if table in db_tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table};") # tbl name checked against schema list
                count = cursor.fetchone()[0]
                report["table_row_counts"][table] = count
            else:
                report["missing_tables"].append(table)
                report["errors"].append(f"Table '{table}' is missing from database.")
                report["status"] = "INVALID"

    except Exception as e:
        report["status"] = "ERROR"
        report["errors"].append(str(e))
    finally:
        conn.close()

    logger.info(f"Database validation complete. Status: {report['status']}")
    return report


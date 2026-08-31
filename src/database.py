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

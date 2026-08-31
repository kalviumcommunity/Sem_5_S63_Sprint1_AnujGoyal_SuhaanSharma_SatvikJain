"""
Data Storage and Export Module for Learning Analytics.
Provides reusable functions to save processed datasets to CSV, JSON, and SQLite database.
"""

from pathlib import Path
from typing import Optional, Union
import sqlite3
import pandas as pd
from src.utils import PROCESSED_DATA_DIR, DB_PATH, setup_logger, timed_step, DataExportError

logger = setup_logger(__name__)


@timed_step("Save DataFrame")
def save_dataframe(
    df: pd.DataFrame,
    file_path: Union[str, Path],
    format: Optional[str] = None,
    index: bool = False,
    **kwargs
) -> Path:
    """
    Saves a DataFrame to disk in CSV or JSON format.
    Automatically creates parent directories if needed.
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    file_format = format.lower() if format else path.suffix.lstrip(".").lower()
    
    try:
        if file_format == "csv":
            df.to_csv(path, index=index, **kwargs)
        elif file_format == "json":
            df.to_json(path, orient="records", indent=2, **kwargs)
        else:
            raise DataExportError(f"Unsupported export format '{file_format}' for path {path}")
        
        logger.info(f"Successfully saved {len(df)} rows to {path}")
        return path
    except Exception as e:
        if isinstance(e, DataExportError):
            raise e
        raise DataExportError(f"Failed saving dataset to {path}: {e}") from e


def export_processed_dataset(
    df: pd.DataFrame,
    filename: str,
    directory: Optional[Path] = None,
    **kwargs
) -> Path:
    """Exports a DataFrame to the processed data directory."""
    target_dir = directory or PROCESSED_DATA_DIR
    target_path = target_dir / filename
    return save_dataframe(df, target_path, **kwargs)


@timed_step("Save to SQLite Database")
def save_to_database(
    df: pd.DataFrame,
    table_name: str,
    db_path: Optional[Path] = None,
    if_exists: str = "replace",
    index: bool = False
) -> None:
    """
    Writes a DataFrame into the project's SQLite database table.
    """
    target_db = db_path or DB_PATH
    target_db.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with sqlite3.connect(str(target_db)) as conn:
            df.to_sql(table_name, conn, if_exists=if_exists, index=index)
        logger.info(f"Successfully written {len(df)} records into SQLite table '{table_name}'.")
    except Exception as e:
        raise DataExportError(f"Failed to write DataFrame to database table '{table_name}': {e}") from e

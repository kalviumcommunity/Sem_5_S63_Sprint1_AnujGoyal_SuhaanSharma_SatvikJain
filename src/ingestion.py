"""
Data Ingestion Module for Learning Analytics.
Provides reusable functions to load datasets from multiple file formats.
"""

from pathlib import Path
from typing import Dict, Optional, Union
import pandas as pd
from src.utils import RAW_DATA_DIR, setup_logger, timed_step, DataLoadError

logger = setup_logger(__name__)


@timed_step("Load Dataset")
def load_dataset(
    file_path: Union[str, Path],
    format: Optional[str] = None,
    **kwargs
) -> pd.DataFrame:
    """
    Loads a dataset from disk into a Pandas DataFrame.
    Supports CSV and JSON file formats.
    """
    path = Path(file_path)
    if not path.exists():
        raise DataLoadError(f"Dataset file not found at: {path}")

    file_format = format.lower() if format else path.suffix.lstrip(".").lower()
    
    try:
        if file_format == "csv":
            df = pd.read_csv(path, **kwargs)
        elif file_format == "json":
            df = pd.read_json(path, **kwargs)
        elif file_format in ("xlsx", "xls"):
            df = pd.read_excel(path, **kwargs)
        else:
            raise DataLoadError(f"Unsupported dataset format '{file_format}' for file {path.name}")
        
        logger.info(f"Successfully loaded {len(df)} rows and {len(df.columns)} columns from {path.name}")
        return df
    except Exception as e:
        if isinstance(e, DataLoadError):
            raise e
        raise DataLoadError(f"Error loading {path.name}: {str(e)}") from e


def load_raw_dataset(filename: str, directory: Optional[Path] = None, **kwargs) -> pd.DataFrame:
    """Loads a file from the raw data directory with fallback if not present."""
    raw_dir = directory or RAW_DATA_DIR
    target_file = raw_dir / filename
    if not target_file.exists():
        logger.warning(f"File {target_file} does not exist. Returning empty DataFrame.")
        return pd.DataFrame()
    return load_dataset(target_file, **kwargs)


def load_all_raw_data(directory: Optional[Path] = None) -> Dict[str, pd.DataFrame]:
    """Loads all standard raw project datasets into a dictionary."""
    dataset_files = {
        "students": "students.csv",
        "sessions": "sessions.csv",
        "quizzes": "quizzes.csv",
        "courses": "courses.csv"
    }
    raw_dir = directory or RAW_DATA_DIR
    data = {}
    for name, filename in dataset_files.items():
        file_path = raw_dir / filename
        if file_path.exists():
            data[name] = load_dataset(file_path)
        else:
            logger.debug(f"Dataset '{name}' ({filename}) not present yet in {raw_dir}")
            data[name] = pd.DataFrame()
    return data

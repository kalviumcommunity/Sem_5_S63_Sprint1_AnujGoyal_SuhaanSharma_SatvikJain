"""
Data Ingestion Module for Learning Analytics.
Handles loading raw datasets from CSV, JSON, or databases.
"""

from pathlib import Path
from typing import Dict, Optional
import pandas as pd
from src.utils import RAW_DATA_DIR, setup_logger

logger = setup_logger(__name__)


def load_raw_dataset(filename: str, directory: Optional[Path] = None) -> pd.DataFrame:
    """Loads a raw dataset file from the raw data directory."""
    raw_dir = directory or RAW_DATA_DIR
    file_path = raw_dir / filename
    if not file_path.exists():
        logger.warning(f"File {file_path} does not exist.")
        return pd.DataFrame()
    logger.info(f"Loading raw dataset from {file_path}")
    return pd.read_csv(file_path)


def load_all_raw_data() -> Dict[str, pd.DataFrame]:
    """Loads all standard raw datasets if available."""
    dataset_files = {
        "students": "students.csv",
        "sessions": "sessions.csv",
        "quizzes": "quizzes.csv",
        "courses": "courses.csv"
    }
    data = {}
    for name, filename in dataset_files.items():
        data[name] = load_raw_dataset(filename)
    return data

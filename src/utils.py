"""
Utility functions and project configuration for Learning Analytics.
"""

import os
from pathlib import Path
import logging

# Project Root Directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Directory Paths
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
DATABASE_DIR = DATA_DIR / "database"
DB_PATH = DATABASE_DIR / "learning_analytics.db"
REPORTS_DIR = PROJECT_ROOT / "reports"
CHARTS_DIR = REPORTS_DIR / "charts"
INSIGHTS_DIR = REPORTS_DIR / "insights"
SQL_DIR = PROJECT_ROOT / "sql"


def setup_logger(name: str = "learning_analytics", level: int = logging.INFO) -> logging.Logger:
    """Configures and returns a standard logger for the project."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(level)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            fmt="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


def ensure_directories_exist() -> None:
    """Ensures all standard project directories exist."""
    directories = [
        RAW_DATA_DIR,
        PROCESSED_DATA_DIR,
        DATABASE_DIR,
        CHARTS_DIR,
        INSIGHTS_DIR,
        SQL_DIR,
    ]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

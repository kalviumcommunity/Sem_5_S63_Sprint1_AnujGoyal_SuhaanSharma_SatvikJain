"""
Utility functions, custom exceptions, and project configuration for Learning Analytics.
"""

import os
import time
import functools
import logging
from pathlib import Path
from typing import Callable, Any, Optional

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


class DataWorkflowError(Exception):
    """Base exception class for data workflow errors."""
    pass


class DataLoadError(DataWorkflowError):
    """Raised when loading a dataset fails."""
    pass


class TransformationError(DataWorkflowError):
    """Raised when transforming a dataset fails."""
    pass


class DataExportError(DataWorkflowError):
    """Raised when exporting or saving a dataset fails."""
    pass


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


def timed_step(step_name: Optional[str] = None):
    """Decorator to measure and log execution time of a workflow step."""
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            logger = setup_logger(func.__module__)
            name = step_name or func.__name__
            logger.info(f"Starting step: '{name}'...")
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                logger.info(f"Completed step: '{name}' in {elapsed:.3f}s")
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(f"Failed step: '{name}' after {elapsed:.3f}s: {e}")
                raise
        return wrapper
    return decorator

"""
Learning Behaviour & Course Completion Analytics
Main Application Entry Point
"""

import sys
from pathlib import Path
from src.utils import setup_logger, ensure_directories_exist, DB_PATH
from src.database import init_database
from src.pipeline import run_pipeline

# Configure UTF-8 encoding for standard output on Windows consoles
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

logger = setup_logger("main")


def print_banner() -> None:
    banner = """
================================================================================
* Learning Behaviour & Course Completion Intelligence
  Production Analytics & Dropout Risk Detection System
================================================================================
"""
    print(banner)


def check_environment() -> bool:
    """Verifies that core modules and dependencies are operational."""
    logger.info(f"Python Version: {sys.version.split()[0]}")
    try:
        import pandas as pd
        import numpy as np
        import plotly
        import streamlit
        logger.info(f"Pandas version: {pd.__version__}")
        logger.info(f"NumPy version: {np.__version__}")
        logger.info(f"Plotly version: {plotly.__version__}")
        logger.info(f"Streamlit version: {streamlit.__version__}")
        return True
    except ImportError as e:
        logger.error(f"Missing required dependency: {e}")
        return False


def main() -> int:
    """Main execution entry point."""
    print_banner()
    logger.info("Initializing project workspace and directories...")
    ensure_directories_exist()

    logger.info("Verifying Python environment and dependencies...")
    env_ok = check_environment()
    if not env_ok:
        logger.error("Environment verification failed. Please check dependencies.")
        return 1

    logger.info(f"Initializing SQLite database schema at: {DB_PATH}")
    init_database()

    logger.info("Executing baseline analytics pipeline...")
    result = run_pipeline()
    logger.info(f"Pipeline execution completed with status: {result.get('status')}")

    print("\n[OK] System status: Ready. Workspace and environment configured successfully.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

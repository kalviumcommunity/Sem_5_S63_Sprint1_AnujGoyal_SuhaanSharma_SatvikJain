"""
End-to-End Analytics Pipeline Orchestrator.
Coordinates ingestion, validation, cleaning, feature engineering, and database loading.
"""

from typing import Dict, Any
import pandas as pd
from src.utils import setup_logger, ensure_directories_exist
from src.ingestion import load_all_raw_data
from src.cleaning import clean_dataframe
from src.database import init_database

logger = setup_logger(__name__)


def run_pipeline() -> Dict[str, Any]:
    """Executes the baseline data pipeline."""
    logger.info("Starting Learning Analytics Pipeline...")
    ensure_directories_exist()
    init_database()
    
    raw_data = load_all_raw_data()
    cleaned_data = {}
    for name, df in raw_data.items():
        if not df.empty:
            cleaned_data[name] = clean_dataframe(df)
            
    logger.info("Pipeline run finished successfully.")
    return {
        "status": "SUCCESS",
        "raw_datasets_loaded": list(raw_data.keys()),
        "processed_datasets": list(cleaned_data.keys())
    }


if __name__ == "__main__":
    result = run_pipeline()
    print("Pipeline Execution Result:", result)

"""
End-to-End Analytics Pipeline Orchestrator.
Coordinates ingestion, validation, cleaning, feature engineering, and database loading.
"""

from typing import Dict, Any, Optional
from pathlib import Path
import pandas as pd
from src.utils import setup_logger, ensure_directories_exist
from src.database import init_database
from src.workflow import DataWorkflow

logger = setup_logger(__name__)


def run_pipeline(source_data: Optional[Dict[str, pd.DataFrame]] = None) -> Dict[str, Any]:
    """Executes the data pipeline using the modular DataWorkflow."""
    logger.info("Starting Learning Analytics Pipeline...")
    ensure_directories_exist()
    init_database()
    
    workflow = DataWorkflow(name="CourseCompletionPipeline")
    result = workflow.run_full_pipeline(source=source_data)
    
    logger.info("Pipeline run finished successfully.")
    return {
        "status": result["status"],
        "raw_datasets_loaded": result["datasets_loaded"],
        "processed_datasets": result["datasets_transformed"]
    }


if __name__ == "__main__":
    result = run_pipeline()
    print("Pipeline Execution Result:", result)

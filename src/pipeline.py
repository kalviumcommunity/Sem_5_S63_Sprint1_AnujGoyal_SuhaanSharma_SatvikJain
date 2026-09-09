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


def run_pipeline(
    source_data: Optional[Dict[str, pd.DataFrame]] = None,
    save_to_db: bool = True
) -> Dict[str, Any]:
    """Executes the data pipeline using the modular DataWorkflow and persists datasets into SQLite database."""
    from src.database import validate_database_insertion

    logger.info("Starting Learning Analytics Pipeline...")
    ensure_directories_exist()
    init_database()

    workflow = DataWorkflow(name="CourseCompletionPipeline")
    result = workflow.run_full_pipeline(source=source_data, save_to_db=save_to_db)
    db_report = validate_database_insertion() if save_to_db else {"status": "SKIPPED"}

    logger.info("Pipeline run finished successfully.")
    return {
        "status": result["status"],
        "raw_datasets_loaded": result["datasets_loaded"],
        "processed_datasets": result["datasets_transformed"],
        "database_status": db_report.get("status"),
        "table_row_counts": db_report.get("table_row_counts", {})
    }


if __name__ == "__main__":
    result = run_pipeline()
    print("Pipeline Execution Result:", result)

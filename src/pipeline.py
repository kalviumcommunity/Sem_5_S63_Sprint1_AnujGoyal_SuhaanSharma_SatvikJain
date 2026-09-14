"""Reliable end-to-end Learning Analytics pipeline entry point."""

from typing import Dict, Any, Optional
from pathlib import Path
import pandas as pd
from src.utils import RAW_DATA_DIR, REPORTS_DIR, DB_PATH, setup_logger, ensure_directories_exist
from src.ingestion import ingest_all_entities
from src.validation import validate_intake_pipeline
from src.cleaning import clean_dataframe
from src.merging import build_student_360_dataset
from src.features import engineer_behavioral_features
from src.database import (
    create_database_indexes,
    execute_analytical_views,
    execute_business_metrics,
    init_database,
    load_processed_data_to_sqlite,
    validate_database_insertion,
)
from src.export import export_all_analytical_outputs

logger = setup_logger(__name__)


def run_pipeline(
    source_data: Optional[Dict[str, pd.DataFrame]] = None,
    save_to_db: bool = True,
    source_dir: Optional[Path] = None,
    db_path: Optional[Path] = None,
    output_dir: Optional[Path] = None,
    generate_outputs: bool = True,
) -> Dict[str, Any]:
    """Execute ingestion through output generation as one repeatable operation.

    The default SQLite write mode is ``replace`` so rerunning the same source
    does not duplicate rows. A dictionary of DataFrames is accepted for tests
    and programmatic callers; otherwise the standard raw-data directory is used.
    """
    target_db = Path(db_path or DB_PATH)
    target_output = Path(output_dir or REPORTS_DIR)
    logger.info("Starting Learning Analytics Pipeline...")
    ensure_directories_exist()

    try:
        logger.info("Stage 1/7: ingesting source datasets")
        raw_datasets = source_data if source_data is not None else ingest_all_entities(
            directory=source_dir or RAW_DATA_DIR,
            validate_schema=False,
        )
        populated = {name: dataframe for name, dataframe in raw_datasets.items() if dataframe is not None and not dataframe.empty}
        if not populated:
            message = "No populated source datasets found; pipeline stages skipped."
            logger.warning(message)
            return {
                "status": "SUCCESS",
                "message": message,
                "stages": {"ingestion": "SKIPPED", "validation": "SKIPPED", "cleaning": "SKIPPED", "feature_engineering": "SKIPPED", "analysis": "SKIPPED", "sqlite_update": "SKIPPED", "output_generation": "SKIPPED"},
                "raw_datasets_loaded": [],
                "processed_datasets": [],
                "database_status": "SKIPPED",
                "table_row_counts": {},
                "output_paths": {},
            }

        logger.info("Stage 2/7: validating source datasets")
        validation = validate_intake_pipeline(populated, raise_on_error=True)

        logger.info("Stage 3/7: cleaning datasets")
        cleaned = {
            name: clean_dataframe(dataframe, entity_name=name)
            for name, dataframe in populated.items()
        }

        required_entities = {"students", "courses", "sessions", "quizzes"}
        missing_entities = sorted(required_entities - set(cleaned))
        if missing_entities:
            raise ValueError(f"Feature engineering requires source entities: {', '.join(missing_entities)}")

        logger.info("Stage 4/7: building Student 360 features")
        student_360, join_report = build_student_360_dataset(
            cleaned["students"], cleaned["courses"], cleaned["sessions"], cleaned["quizzes"]
        )
        behavioural_features = engineer_behavioral_features(student_360)

        processed = {**cleaned, "behavioural_features": behavioural_features}
        output_paths: Dict[str, str] = {}
        database_status = "SKIPPED"
        table_row_counts: Dict[str, int] = {}

        if save_to_db:
            logger.info("Stage 5/7: updating SQLite tables")
            init_database(db_path=target_db)
            inserted = load_processed_data_to_sqlite(processed, db_path=target_db, if_exists="replace")
            create_database_indexes(db_path=target_db)
            db_report = validate_database_insertion(db_path=target_db, expected_tables=list(processed))
            database_status = db_report.get("status", "UNKNOWN")
            table_row_counts = db_report.get("table_row_counts", {})
        else:
            inserted = {}

        logger.info("Stage 6/7: running analytical queries")
        analysis = {}
        if save_to_db:
            analysis = {
                "kpis": execute_business_metrics(db_path=target_db).get("kpis", {}),
                "views": {name: len(dataframe) for name, dataframe in execute_analytical_views(db_path=target_db).items()},
            }

        if generate_outputs and save_to_db:
            logger.info("Stage 7/7: generating analytical outputs")
            output_paths = {name: str(path) for name, path in export_all_analytical_outputs(db_path=target_db, export_dir=target_output).items()}

        logger.info("Learning Analytics Pipeline completed successfully.")
        return {
            "status": "SUCCESS",
            "message": "End-to-end data pipeline completed successfully.",
            "stages": {"ingestion": "SUCCESS", "validation": validation.get("status", "SUCCESS"), "cleaning": "SUCCESS", "feature_engineering": "SUCCESS", "analysis": "SUCCESS" if save_to_db else "SKIPPED", "sqlite_update": database_status, "output_generation": "SUCCESS" if output_paths else "SKIPPED"},
            "raw_datasets_loaded": list(populated),
            "processed_datasets": list(processed),
            "database_status": database_status,
            "table_row_counts": table_row_counts,
            "inserted_row_counts": inserted,
            "analysis": analysis,
            "join_report": join_report.to_dict() if hasattr(join_report, "to_dict") else {},
            "output_paths": output_paths,
        }
    except Exception as error:
        logger.exception("Learning Analytics Pipeline failed: %s", error)
        return {
            "status": "FAILURE",
            "message": f"Pipeline failed: {error}",
            "error": str(error),
            "stages": {},
            "raw_datasets_loaded": [],
            "processed_datasets": [],
            "database_status": "FAILED",
            "table_row_counts": {},
            "output_paths": {},
        }


if __name__ == "__main__":
    result = run_pipeline()
    print("Pipeline Execution Result:", result)

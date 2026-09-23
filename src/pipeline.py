"""Reliable, repeatable end-to-end Learning Analytics pipeline entry point."""

import json
import sys
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple

import pandas as pd

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.consistency import validate_all_consistency
from src.database import (
    create_database_indexes,
    execute_analytical_views,
    execute_business_metrics,
    init_database,
    load_processed_data_to_sqlite,
    validate_database_insertion,
)
from src.datetime_pipeline import transform_all_datetimes
from src.deduplication import deduplicate_dataset
from src.export import export_all_analytical_outputs
from src.features import engineer_behavioral_features
from src.imputation import impute_dataset
from src.ingestion import ingest_all_entities
from src.merging import build_student_360_dataset
from src.outliers import tag_dataset_outliers
from src.profiling import profile_dataset
from src.standardization import standardize_entity
from src.storage import export_processed_dataset
from src.text_cleaning import clean_text_dataframe
from src.utils import (
    DB_PATH,
    PROCESSED_DATA_DIR,
    RAW_DATA_DIR,
    REPORTS_DIR,
    ValidationError,
    ensure_directories_exist,
    setup_logger,
)
from src.validation import validate_intake_pipeline

logger = setup_logger(__name__)

REQUIRED_ENTITIES = ("students", "courses", "sessions", "quizzes")
STAGE_ORDER = (
    "ingestion",
    "source_validation",
    "profiling",
    "missing_value_handling",
    "type_standardisation",
    "duplicate_handling",
    "string_cleaning",
    "datetime_transformation",
    "outlier_detection",
    "consistency_validation",
    "multi_source_merging",
    "feature_engineering",
    "behavioural_analysis",
    "risk_identification",
    "sqlite_update",
    "kpi_output_generation",
)


def _empty_result(message: str, stages: Dict[str, str]) -> Dict[str, Any]:
    return {
        "status": "FAILURE",
        "message": message,
        "error": message,
        "failed_stage": next((name for name, state in stages.items() if state == "FAILED"), None),
        "stages": stages,
        "raw_datasets_loaded": [],
        "processed_datasets": [],
        "database_status": "FAILED",
        "table_row_counts": {},
        "output_paths": {},
    }


def run_pipeline(
    source_data: Optional[Dict[str, pd.DataFrame]] = None,
    save_to_db: bool = True,
    source_dir: Optional[Path] = None,
    db_path: Optional[Path] = None,
    output_dir: Optional[Path] = None,
    processed_dir: Optional[Path] = None,
    generate_outputs: bool = True,
) -> Dict[str, Any]:
    """Execute every analytics stage once and return an auditable run result.

    ``source_data`` is useful for programmatic callers and tests. When omitted,
    the four named entity files are loaded from ``source_dir`` or ``data/raw``.
    SQLite writes and processed-file exports use replacement semantics so the
    same input can be run repeatedly without accumulating duplicate rows.
    """
    target_db = Path(db_path or DB_PATH)
    target_output = Path(output_dir or REPORTS_DIR)
    target_processed = Path(processed_dir or PROCESSED_DATA_DIR)
    stages = {name: "PENDING" for name in STAGE_ORDER}
    current_stage = "ingestion"

    def stage(name: str, operation: Callable[[], Any]) -> Any:
        nonlocal current_stage
        current_stage = name
        logger.info("Stage %s/%s started: %s", STAGE_ORDER.index(name) + 1, len(STAGE_ORDER), name)
        stages[name] = "RUNNING"
        try:
            result = operation()
        except Exception:
            stages[name] = "FAILED"
            logger.exception("Stage failed: %s", name)
            raise
        stages[name] = "SUCCESS"
        logger.info("Stage %s completed successfully: %s", name, name)
        return result

    try:
        ensure_directories_exist()
        raw_datasets = stage(
            "ingestion",
            lambda: source_data if source_data is not None else ingest_all_entities(
                directory=source_dir or RAW_DATA_DIR,
                validate_schema=False,
            ),
        )
        raw_datasets = {
            name: dataframe.copy()
            for name, dataframe in raw_datasets.items()
            if dataframe is not None and not dataframe.empty
        }
        validation = stage(
            "source_validation",
            lambda: _validate_required_sources(raw_datasets),
        )
        profiles = stage(
            "profiling",
            lambda: {name: profile_dataset(df, dataset_name=name) for name, df in raw_datasets.items()},
        )

        datasets, imputation_reports = stage(
            "missing_value_handling",
            lambda: _apply_dataset_step(raw_datasets, impute_dataset),
        )
        datasets = stage(
            "type_standardisation",
            lambda: {
                name: standardize_entity(df, entity_name=name)
                for name, df in datasets.items()
            },
        )
        datasets, deduplication_reports = stage(
            "duplicate_handling",
            lambda: _apply_dataset_step(datasets, deduplicate_dataset),
        )
        datasets = stage(
            "string_cleaning",
            lambda: {
                name: clean_text_dataframe(df, entity_name=name)
                for name, df in datasets.items()
            },
        )
        datasets = stage("datetime_transformation", lambda: transform_all_datetimes(datasets))
        datasets, outlier_reports = stage(
            "outlier_detection",
            lambda: _apply_dataset_step(datasets, tag_dataset_outliers),
        )

        datasets, consistency_reports = stage(
            "consistency_validation",
            lambda: _validate_consistency_or_fail(datasets),
        )
        student_360, join_report = stage(
            "multi_source_merging",
            lambda: build_student_360_dataset(
                datasets["students"],
                datasets["courses"],
                datasets["sessions"],
                datasets["quizzes"],
            ),
        )
        behavioural_features = stage(
            "feature_engineering",
            lambda: engineer_behavioral_features(student_360),
        )
        processed = {**datasets, "behavioural_features": behavioural_features}
        stage("behavioural_analysis", lambda: _require_non_empty(behavioural_features, "behavioural features"))
        stage("risk_identification", lambda: _require_columns(behavioural_features, ["dropout_risk_score", "dropout_risk_level"]))

        inserted: Dict[str, int] = {}
        database_status = "SKIPPED"
        table_row_counts: Dict[str, int] = {}
        analysis: Dict[str, Any] = {}
        if save_to_db:
            inserted, database_status, table_row_counts = stage(
                "sqlite_update",
                lambda: _update_database(processed, target_db),
            )
            analysis, output_paths = stage(
                "kpi_output_generation",
                lambda: _generate_outputs(
                    target_db,
                    target_output,
                    target_processed,
                    processed,
                    generate_outputs,
                ),
            )
        else:
            stages["sqlite_update"] = "SKIPPED"
            stages["kpi_output_generation"] = "SKIPPED"
            output_paths = {}

        logger.info("Learning Analytics Pipeline completed successfully.")
        result = {
            "status": "SUCCESS",
            "message": "End-to-end data pipeline completed successfully.",
            "stages": stages,
            "raw_datasets_loaded": list(raw_datasets),
            "processed_datasets": list(processed),
            "database_status": database_status,
            "table_row_counts": table_row_counts,
            "inserted_row_counts": inserted,
            "analysis": analysis,
            "profiles": {name: profile.to_dict() for name, profile in profiles.items()},
            "validation": validation,
            "imputation": {name: report.to_dict() for name, report in imputation_reports.items()},
            "deduplication": {name: report.to_dict() for name, report in deduplication_reports.items()},
            "outliers": {name: report.to_dict() for name, report in outlier_reports.items()},
            "consistency": {name: report.to_dict() for name, report in consistency_reports.items()},
            "join_report": join_report.to_dict() if hasattr(join_report, "to_dict") else {},
            "output_paths": output_paths,
        }
        # Preserve names returned by the previous public pipeline contract.
        result["stages"]["validation"] = validation.get("status", "SUCCESS")
        result["stages"]["output_generation"] = "SUCCESS" if output_paths else "SKIPPED"
        return result
    except Exception as error:
        logger.exception("Pipeline failed at stage '%s': %s", current_stage, error)
        stages[current_stage] = "FAILED"
        result = _empty_result(f"Pipeline failed during {current_stage}: {error}", stages)
        result["stages"]["validation"] = stages.get("source_validation", "PENDING")
        result["stages"]["output_generation"] = stages.get("kpi_output_generation", "PENDING")
        result["raw_datasets_loaded"] = list(raw_datasets) if "raw_datasets" in locals() else []
        return result


def _apply_dataset_step(
    datasets: Dict[str, pd.DataFrame],
    function: Callable[..., Tuple[pd.DataFrame, Any]],
) -> Tuple[Dict[str, pd.DataFrame], Dict[str, Any]]:
    transformed: Dict[str, pd.DataFrame] = {}
    reports: Dict[str, Any] = {}
    for name, dataframe in datasets.items():
        transformed[name], reports[name] = function(dataframe, entity_name=name)
    return transformed, reports


def _validate_required_sources(datasets: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    missing_entities = sorted(set(REQUIRED_ENTITIES) - set(datasets))
    if missing_entities:
        raise ValidationError(
            "Pipeline requires source entities; missing required data: "
            + ", ".join(missing_entities)
            + ". Expected students, courses, sessions, and quizzes source files."
        )
    return validate_intake_pipeline(datasets, raise_on_error=True)


def _validate_consistency_or_fail(
    datasets: Dict[str, pd.DataFrame],
) -> Tuple[Dict[str, pd.DataFrame], Dict[str, Any]]:
    validated, reports = validate_all_consistency(datasets)
    failures = {
        name: report.invalid_records
        for name, report in reports.items()
        if report.invalid_records
    }
    if failures:
        raise ValidationError(f"Data consistency validation failed: {failures}")
    return validated, reports


def _require_non_empty(dataframe: pd.DataFrame, label: str) -> pd.DataFrame:
    if dataframe is None or dataframe.empty:
        raise ValidationError(f"{label.capitalize()} stage produced no records.")
    return dataframe


def _require_columns(dataframe: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    missing = sorted(set(columns) - set(dataframe.columns))
    if missing:
        raise ValidationError(f"Risk identification output is missing columns: {missing}")
    return dataframe


def _update_database(
    processed: Dict[str, pd.DataFrame],
    db_path: Path,
) -> Tuple[Dict[str, int], str, Dict[str, int]]:
    init_database(db_path=db_path)
    inserted = load_processed_data_to_sqlite(processed, db_path=db_path, if_exists="replace")
    create_database_indexes(db_path=db_path)
    db_report = validate_database_insertion(db_path=db_path, expected_tables=list(processed))
    if db_report.get("status") != "VALID":
        raise ValidationError(f"SQLite validation failed: {db_report.get('errors', [])}")
    return inserted, db_report["status"], db_report.get("table_row_counts", {})


def _build_analysis(db_path: Path) -> Dict[str, Any]:
    metrics = execute_business_metrics(db_path=db_path)
    views = execute_analytical_views(db_path=db_path)
    return {
        "kpis": metrics.get("kpis", {}),
        "views": {name: len(dataframe) for name, dataframe in views.items()},
    }


def _generate_outputs(
    db_path: Path,
    output_dir: Path,
    processed_dir: Path,
    processed: Dict[str, pd.DataFrame],
    generate_outputs: bool,
) -> Tuple[Dict[str, Any], Dict[str, str]]:
    analysis = _build_analysis(db_path)
    if not generate_outputs:
        return analysis, {}
    exported = export_all_analytical_outputs(db_path=db_path, export_dir=output_dir)
    processed_paths = {
        name: export_processed_dataset(df, f"{name}.csv", directory=processed_dir)
        for name, df in processed.items()
    }
    output_paths = {
        **{name: str(path) for name, path in exported.items()},
        **{f"processed_{name}": str(path) for name, path in processed_paths.items()},
    }
    return analysis, output_paths


def main() -> int:
    """Run the default data pipeline and return a process exit code."""
    result = run_pipeline()
    print(json.dumps({"status": result["status"], "message": result["message"], "stages": result["stages"]}, indent=2))
    return 0 if result["status"] == "SUCCESS" else 1


if __name__ == "__main__":
    sys.exit(main())

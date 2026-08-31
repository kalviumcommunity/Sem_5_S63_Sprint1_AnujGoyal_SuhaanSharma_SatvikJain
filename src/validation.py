"""
Dataset Intake & Source Validation Module for Learning Analytics.
Provides reusable functions to validate file existence, formats, schema requirements,
empty datasets, row thresholds, and expected source structures before processing.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import pandas as pd
from src.utils import setup_logger, timed_step, ValidationError

logger = setup_logger(__name__)

# Supported File Formats for Data Intake
SUPPORTED_FORMATS = [".csv", ".json", ".xlsx", ".xls"]

# Standard Project Entity Schemas (Required Columns)
ENTITY_SCHEMAS: Dict[str, List[str]] = {
    "students": [
        "student_id",
        "registration_date",
        "age",
        "gender",
        "education_level",
        "device_type",
        "target_course_id",
        "completion_status"
    ],
    "sessions": [
        "session_id",
        "student_id",
        "course_id",
        "session_start",
        "session_end",
        "duration_minutes",
        "active_minutes",
        "idle_minutes"
    ],
    "quizzes": [
        "quiz_attempt_id",
        "student_id",
        "course_id",
        "quiz_id",
        "attempt_number",
        "attempt_date",
        "score_percentage",
        "time_taken_minutes",
        "passed"
    ],
    "courses": [
        "course_id",
        "course_title",
        "category",
        "total_modules",
        "total_quizzes",
        "estimated_duration_hours"
    ]
}


@dataclass
class ValidationResult:
    """Represents the structured outcome of a validation check."""
    is_valid: bool
    dataset_name: str
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    row_count: int = 0
    column_count: int = 0
    missing_columns: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Converts the validation result to a standard dictionary."""
        return {
            "status": "VALID" if self.is_valid else "INVALID",
            "dataset_name": self.dataset_name,
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "row_count": self.row_count,
            "column_count": self.column_count,
            "missing_columns": self.missing_columns
        }


@timed_step("Validate File Source")
def validate_file_source(
    file_path: Union[str, Path],
    supported_formats: Optional[List[str]] = None
) -> ValidationResult:
    """
    Validates physical file existence, readability, and extension.
    """
    path = Path(file_path)
    allowed = supported_formats or SUPPORTED_FORMATS
    errors = []

    if not path.exists():
        errors.append(f"Source file does not exist: {path}")
        logger.error(errors[-1])
        return ValidationResult(is_valid=False, dataset_name=path.name, errors=errors)

    if not path.is_file():
        errors.append(f"Specified path is not a file: {path}")
        logger.error(errors[-1])
        return ValidationResult(is_valid=False, dataset_name=path.name, errors=errors)

    if path.stat().st_size == 0:
        errors.append(f"File is 0 bytes (empty file): {path}")
        logger.error(errors[-1])
        return ValidationResult(is_valid=False, dataset_name=path.name, errors=errors)

    if path.suffix.lower() not in allowed:
        errors.append(f"Unsupported file format '{path.suffix}'. Expected one of: {allowed}")
        logger.error(errors[-1])
        return ValidationResult(is_valid=False, dataset_name=path.name, errors=errors)

    logger.info(f"File source validation PASSED for: {path.name}")
    return ValidationResult(is_valid=True, dataset_name=path.name)


@timed_step("Validate Dataset Schema")
def validate_dataset_schema(
    df: pd.DataFrame,
    required_columns: List[str],
    dataset_name: str = "Dataset",
    min_rows: int = 1
) -> ValidationResult:
    """
    Validates DataFrame structure, required columns, and minimum row count.
    """
    errors = []
    warnings = []

    if df is None:
        errors.append("DataFrame is None.")
        return ValidationResult(is_valid=False, dataset_name=dataset_name, errors=errors)

    row_count = len(df)
    col_count = len(df.columns)

    if df.empty or row_count == 0:
        errors.append(f"Dataset '{dataset_name}' is empty (0 rows).")

    if col_count == 0:
        errors.append(f"Dataset '{dataset_name}' contains 0 columns.")

    if row_count < min_rows and row_count > 0:
        errors.append(f"Dataset '{dataset_name}' has {row_count} rows, below required minimum of {min_rows}.")

    # Column check (ignoring leading/trailing whitespace and case for matching)
    actual_cols_clean = [str(c).strip().lower() for c in df.columns]
    missing_cols = []
    for req_col in required_columns:
        req_clean = req_col.strip().lower()
        if req_clean not in actual_cols_clean:
            missing_cols.append(req_col)

    if missing_cols:
        errors.append(f"Missing required columns in '{dataset_name}': {missing_cols}")

    is_valid = len(errors) == 0
    result = ValidationResult(
        is_valid=is_valid,
        dataset_name=dataset_name,
        errors=errors,
        warnings=warnings,
        row_count=row_count,
        column_count=col_count,
        missing_columns=missing_cols
    )

    if not is_valid:
        logger.error(f"Schema validation FAILED for '{dataset_name}': {errors}")
    else:
        logger.info(f"Schema validation PASSED for '{dataset_name}' ({row_count} rows, {col_count} cols).")

    return result


def validate_dataframe(
    df: pd.DataFrame,
    required_columns: List[str],
    dataset_name: str = "Dataset",
    min_rows: int = 1
) -> Dict[str, Any]:
    """
    Legacy and simple dictionary interface for DataFrame validation.
    Maintains full backward compatibility.
    """
    res = validate_dataset_schema(
        df=df,
        required_columns=required_columns,
        dataset_name=dataset_name,
        min_rows=min_rows
    )
    result_dict = res.to_dict()
    result_dict["null_counts"] = df.isnull().sum().to_dict() if df is not None and not df.empty else {}
    return result_dict


def validate_entity_dataset(
    df: pd.DataFrame,
    entity_name: str,
    min_rows: int = 1,
    raise_on_error: bool = False
) -> ValidationResult:
    """
    Validates a DataFrame against standard project entity schemas ('students', 'sessions', 'quizzes', 'courses').
    """
    if entity_name not in ENTITY_SCHEMAS:
        raise ValidationError(f"Unknown entity type '{entity_name}'. Expected one of: {list(ENTITY_SCHEMAS.keys())}")

    required_cols = ENTITY_SCHEMAS[entity_name]
    result = validate_dataset_schema(
        df=df,
        required_columns=required_cols,
        dataset_name=entity_name,
        min_rows=min_rows
    )

    if not result.is_valid and raise_on_error:
        raise ValidationError(f"Intake validation failed for entity '{entity_name}': {'; '.join(result.errors)}")

    return result


@timed_step("Validate Intake Pipeline")
def validate_intake_pipeline(
    datasets: Dict[str, pd.DataFrame],
    raise_on_error: bool = False
) -> Dict[str, Any]:
    """
    Validates all ingested entity datasets before downstream pipeline processing.
    """
    overall_valid = True
    reports = {}

    for name, df in datasets.items():
        if name in ENTITY_SCHEMAS:
            val_res = validate_entity_dataset(df, entity_name=name, raise_on_error=False)
        else:
            val_res = validate_dataset_schema(df, required_columns=[], dataset_name=name, min_rows=1)
        
        reports[name] = val_res.to_dict()
        if not val_res.is_valid:
            overall_valid = False

    pipeline_report = {
        "status": "VALID" if overall_valid else "INVALID",
        "overall_valid": overall_valid,
        "entity_reports": reports
    }

    if not overall_valid and raise_on_error:
        failed_entities = [name for name, r in reports.items() if not r["is_valid"]]
        raise ValidationError(f"Intake pipeline validation failed for entities: {failed_entities}")

    return pipeline_report

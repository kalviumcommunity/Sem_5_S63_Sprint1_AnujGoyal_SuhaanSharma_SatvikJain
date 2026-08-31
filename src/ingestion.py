"""
Data Ingestion Module for Learning Analytics.
Provides reusable, robust ingestion functions for CSV and JSON datasets across all project entities:
- students
- courses
- sessions
- quizzes
"""

import json
from pathlib import Path
from typing import Dict, Optional, Union, List, Tuple
import pandas as pd
from src.utils import RAW_DATA_DIR, setup_logger, timed_step, DataLoadError, ValidationError
from src.validation import validate_file_source, validate_entity_dataset, ENTITY_SCHEMAS

logger = setup_logger(__name__)

# Standard Project Entities
SUPPORTED_ENTITIES = ["students", "courses", "sessions", "quizzes"]


def read_json_flexible(file_path: Path, **kwargs) -> pd.DataFrame:
    """
    Reads a JSON file with multi-orientation fallback support (records, split, index, or nested dict).
    """
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except Exception as e:
            raise DataLoadError(f"Malformed or invalid JSON file '{file_path.name}': {e}") from e

    if isinstance(data, list):
        return pd.DataFrame(data)
    elif isinstance(data, dict):
        if "data" in data and isinstance(data["data"], list):
            if "columns" in data and isinstance(data["columns"], list):
                return pd.DataFrame(data["data"], columns=data["columns"])
            return pd.DataFrame(data["data"])
        elif "records" in data and isinstance(data["records"], list):
            return pd.DataFrame(data["records"])
        elif all(isinstance(v, dict) for v in data.values()):
            # Dict of records (e.g. { "S001": {...}, "S002": {...} })
            return pd.DataFrame.from_dict(data, orient="index").reset_index(drop=True)
        else:
            return pd.DataFrame([data])
    else:
        raise DataLoadError(f"Unexpected JSON data structure in '{file_path.name}': {type(data)}")


@timed_step("Load Dataset")
def load_dataset(
    file_path: Union[str, Path],
    format: Optional[str] = None,
    validate_source: bool = False,
    entity_name: Optional[str] = None,
    **kwargs
) -> pd.DataFrame:
    """
    Loads a dataset from disk (CSV or JSON) into a Pandas DataFrame.
    
    Args:
        file_path: Path to the dataset file.
        format: Optional explicit file format ('csv', 'json', 'xlsx').
        validate_source: If True, validates file existence, readability, and non-empty status first.
        entity_name: If provided, validates the ingested dataframe against the entity schema.
        **kwargs: Additional arguments passed to the underlying Pandas reader.
    """
    path = Path(file_path)

    if validate_source:
        val_result = validate_file_source(path)
        if not val_result.is_valid:
            raise DataLoadError(f"Source validation failed: {'; '.join(val_result.errors)}")
    else:
        if not path.exists():
            raise DataLoadError(f"Dataset file not found at: {path}")

    file_format = format.lower() if format else path.suffix.lstrip(".").lower()

    try:
        if file_format == "csv":
            # Attempt standard read with encoding fallback
            try:
                df = pd.read_csv(path, **kwargs)
            except UnicodeDecodeError:
                logger.warning(f"UTF-8 decoding failed for {path.name}, falling back to latin1.")
                df = pd.read_csv(path, encoding="latin1", **kwargs)
        elif file_format == "json":
            df = read_json_flexible(path, **kwargs)
        elif file_format in ("xlsx", "xls"):
            df = pd.read_excel(path, **kwargs)
        else:
            raise DataLoadError(f"Unsupported dataset format '{file_format}' for file {path.name}")

        logger.info(f"Successfully loaded '{path.name}' ({len(df)} rows, {len(df.columns)} columns)")

        # Optional entity schema validation
        if entity_name:
            validate_entity_dataset(df, entity_name=entity_name, raise_on_error=True)

        return df

    except Exception as e:
        if isinstance(e, (DataLoadError, ValidationError)):
            raise e
        raise DataLoadError(f"Failed to ingest dataset '{path.name}': {str(e)}") from e


def ingest_entity(
    entity_name: str,
    directory: Optional[Path] = None,
    preferred_formats: Tuple[str, ...] = (".csv", ".json"),
    validate_schema: bool = True
) -> pd.DataFrame:
    """
    Discovers and ingests a specific entity (students, courses, sessions, quizzes)
    from CSV or JSON format in the specified directory.
    """
    search_dir = directory or RAW_DATA_DIR

    for ext in preferred_formats:
        candidate_file = search_dir / f"{entity_name}{ext}"
        if candidate_file.exists():
            logger.info(f"Found source file for entity '{entity_name}': {candidate_file.name}")
            return load_dataset(
                candidate_file,
                validate_source=True,
                entity_name=entity_name if validate_schema else None
            )

    logger.warning(f"No source file found for entity '{entity_name}' in {search_dir} (Checked: {preferred_formats})")
    return pd.DataFrame()


def ingest_all_entities(
    directory: Optional[Path] = None,
    preferred_formats: Tuple[str, ...] = (".csv", ".json"),
    validate_schema: bool = False
) -> Dict[str, pd.DataFrame]:
    """
    Batch ingests all four core entities (students, courses, sessions, quizzes)
    supporting both CSV and JSON formats.
    """
    search_dir = directory or RAW_DATA_DIR
    datasets = {}

    for entity in SUPPORTED_ENTITIES:
        df = ingest_entity(
            entity_name=entity,
            directory=search_dir,
            preferred_formats=preferred_formats,
            validate_schema=validate_schema
        )
        datasets[entity] = df

    return datasets


# Backward compatible aliases
def load_raw_dataset(filename: str, directory: Optional[Path] = None, **kwargs) -> pd.DataFrame:
    """Loads a raw dataset by filename with fallback if missing."""
    raw_dir = directory or RAW_DATA_DIR
    target_file = raw_dir / filename
    if not target_file.exists():
        logger.warning(f"File {target_file} does not exist. Returning empty DataFrame.")
        return pd.DataFrame()
    return load_dataset(target_file, **kwargs)


def load_all_raw_data(directory: Optional[Path] = None) -> Dict[str, pd.DataFrame]:
    """Loads all standard raw project datasets into a dictionary."""
    return ingest_all_entities(directory=directory, validate_schema=False)

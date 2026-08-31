"""
Python Data Workflow Foundations Pipeline.
Orchestrates reusable loading, inspecting, transforming, and saving of learning analytics data.
"""

from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import pandas as pd
from src.utils import setup_logger, timed_step, ensure_directories_exist
from src.ingestion import load_dataset, load_all_raw_data
from src.inspection import inspect_dataframe
from src.transformation import standardize_column_names, cast_column_types, parse_datetime_columns
from src.storage import save_dataframe, save_to_database

logger = setup_logger(__name__)


class DataWorkflow:
    """
    Reusable data workflow orchestrator following the pipeline principle:
    Load -> Inspect -> Transform -> Export
    """

    def __init__(self, name: str = "LearningAnalyticsWorkflow"):
        self.name = name
        self.raw_data: Dict[str, pd.DataFrame] = {}
        self.inspections: Dict[str, Dict[str, Any]] = {}
        self.transformed_data: Dict[str, pd.DataFrame] = {}
        ensure_directories_exist()

    @timed_step("Workflow Load Step")
    def load(self, source: Union[str, Path, Dict[str, pd.DataFrame]]) -> "DataWorkflow":
        """Loads data from file path or existing dictionary of DataFrames."""
        if isinstance(source, (str, Path)):
            path = Path(source)
            df = load_dataset(path)
            self.raw_data[path.stem] = df
        elif isinstance(source, dict):
            self.raw_data = source
        else:
            self.raw_data = load_all_raw_data()
        return self

    @timed_step("Workflow Inspect Step")
    def inspect(self) -> "DataWorkflow":
        """Performs structured data inspection on all loaded datasets."""
        self.inspections = {}
        for name, df in self.raw_data.items():
            self.inspections[name] = inspect_dataframe(df, dataset_name=name)
        return self

    @timed_step("Workflow Transform Step")
    def transform(
        self,
        type_mappings: Optional[Dict[str, Dict[str, str]]] = None,
        datetime_columns: Optional[Dict[str, List[str]]] = None
    ) -> "DataWorkflow":
        """
        Applies standardized foundational transformations:
        - Column name standardization
        - Type conversions
        - Timestamp parsing
        """
        self.transformed_data = {}
        type_mappings = type_mappings or {}
        datetime_columns = datetime_columns or {}

        for name, df in self.raw_data.items():
            if df.empty:
                self.transformed_data[name] = df.copy()
                continue
            
            # 1. Standardize column names
            transformed = standardize_column_names(df)

            # 2. Apply type mappings if configured
            if name in type_mappings:
                transformed = cast_column_types(transformed, type_mappings[name])

            # 3. Parse date columns if configured
            if name in datetime_columns:
                transformed = parse_datetime_columns(transformed, datetime_columns[name])

            self.transformed_data[name] = transformed
        return self

    @timed_step("Workflow Export Step")
    def export(
        self,
        output_dir: Optional[Path] = None,
        save_to_db: bool = False
    ) -> Dict[str, Path]:
        """Saves all transformed datasets to disk and optionally to SQLite."""
        saved_paths = {}
        for name, df in self.transformed_data.items():
            if not df.empty and output_dir:
                out_path = Path(output_dir) / f"{name}_processed.csv"
                saved_paths[name] = save_dataframe(df, out_path)

            if not df.empty and save_to_db:
                save_to_database(df, table_name=name)
        return saved_paths

    def run_full_pipeline(
        self,
        source: Optional[Union[str, Path, Dict[str, pd.DataFrame]]] = None,
        output_dir: Optional[Path] = None,
        save_to_db: bool = False
    ) -> Dict[str, Any]:
        """Executes full workflow end-to-end and returns run summary."""
        logger.info(f"Executing workflow '{self.name}'...")
        self.load(source if source is not None else {})
        self.inspect()
        self.transform()
        saved = self.export(output_dir=output_dir, save_to_db=save_to_db)

        return {
            "workflow_name": self.name,
            "status": "SUCCESS",
            "datasets_loaded": list(self.raw_data.keys()),
            "datasets_inspected": list(self.inspections.keys()),
            "datasets_transformed": list(self.transformed_data.keys()),
            "saved_outputs": saved
        }

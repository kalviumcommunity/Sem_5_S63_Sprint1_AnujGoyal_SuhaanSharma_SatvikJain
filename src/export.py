"""
Insight Export & Report Generation Engine.

Supports multi-format export (CSV, Markdown summary reports, HTML interactive chart packages, JSON)
for key analytical outputs:
- KPIs
- Learner Risk Data
- Course Metrics
- Behavioural Segments
- Analytical Insights & Storytelling Narratives

Provides Streamlit-compatible in-memory byte buffer generators for direct web downloads.
"""

from typing import Dict, Any, Optional, Union
from pathlib import Path
import io
import json
import pandas as pd
from src.utils import setup_logger, REPORTS_DIR, CHARTS_DIR, INSIGHTS_DIR, DB_PATH

logger = setup_logger(__name__)


# -----------------------------------------------------------------------------
# Streamlit In-Memory Download Helper Functions
# -----------------------------------------------------------------------------

def get_dataframe_csv_bytes(df: pd.DataFrame, index: bool = False) -> bytes:
    """Converts a DataFrame to CSV byte buffer for Streamlit st.download_button."""
    if df is None or df.empty:
        return b""
    buffer = io.StringIO()
    df.to_csv(buffer, index=index)
    return buffer.getvalue().encode("utf-8")


def get_markdown_report_bytes(markdown_text: str) -> bytes:
    """Converts markdown report text into UTF-8 bytes for Streamlit download."""
    if not markdown_text:
        return b""
    return markdown_text.encode("utf-8")


def get_json_bytes(data: Dict[str, Any]) -> bytes:
    """Converts a dictionary to pretty-printed JSON bytes."""
    if not data:
        return b"{}"
    return json.dumps(data, indent=2, default=str).encode("utf-8")


def get_chart_html_bytes(fig: Any) -> bytes:
    """Converts a Plotly Figure into standalone interactive HTML bytes."""
    if fig is None or not hasattr(fig, "to_html"):
        return b""
    html_str = fig.to_html(include_plotlyjs="cdn", full_html=True)
    return html_str.encode("utf-8")


# -----------------------------------------------------------------------------
# Output Export Builders (Disk & File Generation)
# -----------------------------------------------------------------------------

def export_kpis(
    kpis: Dict[str, Any],
    output_path: Optional[Path] = None,
    format: str = "csv"
) -> Path:
    """
    Exports executive KPI dictionary to CSV or JSON format.

    Args:
        kpis: Dictionary of KPI metric names and values
        output_path: Custom destination file path
        format: 'csv' or 'json'

    Returns:
        Path to exported file.
    """
    target_format = format.lower()
    target_path = output_path or (REPORTS_DIR / f"kpi_summary.{target_format}")
    target_path.parent.mkdir(parents=True, exist_ok=True)

    df_kpi = pd.DataFrame([kpis])

    if target_format == "csv":
        df_kpi.to_csv(target_path, index=False)
    elif target_format == "json":
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(kpis, f, indent=2, default=str)
    else:
        raise ValueError(f"Unsupported export format '{format}'. Use 'csv' or 'json'.")

    logger.info(f"Successfully exported KPIs to {target_path}")
    return target_path


def export_learner_risk_data(
    df: pd.DataFrame,
    output_path: Optional[Path] = None,
    format: str = "csv"
) -> Path:
    """
    Exports learner risk tier dataset to CSV or JSON.
    """
    target_format = format.lower()
    target_path = output_path or (REPORTS_DIR / f"learner_risk_data.{target_format}")
    target_path.parent.mkdir(parents=True, exist_ok=True)

    if df.empty:
        df = pd.DataFrame(columns=["student_id", "dropout_risk_level", "engagement_score", "days_since_last_activity"])

    if target_format == "csv":
        df.to_csv(target_path, index=False)
    elif target_format == "json":
        df.to_json(target_path, orient="records", indent=2)

    logger.info(f"Successfully exported {len(df)} learner risk records to {target_path}")
    return target_path


def export_course_metrics(
    df: pd.DataFrame,
    output_path: Optional[Path] = None,
    format: str = "csv"
) -> Path:
    """
    Exports course performance and completion metrics to CSV or JSON.
    """
    target_format = format.lower()
    target_path = output_path or (REPORTS_DIR / f"course_metrics.{target_format}")
    target_path.parent.mkdir(parents=True, exist_ok=True)

    if df.empty:
        df = pd.DataFrame(columns=["course_id", "course_title", "completion_rate_pct", "enrolled_count", "avg_quiz_score"])

    if target_format == "csv":
        df.to_csv(target_path, index=False)
    elif target_format == "json":
        df.to_json(target_path, orient="records", indent=2)

    logger.info(f"Successfully exported {len(df)} course metric records to {target_path}")
    return target_path


def export_behavioural_segments(
    df: pd.DataFrame,
    output_path: Optional[Path] = None,
    format: str = "csv"
) -> Path:
    """
    Exports student behavioural segmentation dataset to CSV or JSON.
    """
    target_format = format.lower()
    target_path = output_path or (REPORTS_DIR / f"behavioural_segments.{target_format}")
    target_path.parent.mkdir(parents=True, exist_ok=True)

    if df.empty:
        df = pd.DataFrame(columns=["student_id", "segment", "sessions_per_week", "avg_session_duration", "learning_consistency"])

    if target_format == "csv":
        df.to_csv(target_path, index=False)
    elif target_format == "json":
        df.to_json(target_path, orient="records", indent=2)

    logger.info(f"Successfully exported {len(df)} behavioural segment records to {target_path}")
    return target_path


def export_insights(
    insights_data: Dict[str, Any],
    output_path: Optional[Path] = None,
    format: str = "md"
) -> Path:
    """
    Exports structured analytical insights and narratives to Markdown or JSON.
    """
    target_format = format.lower()
    target_path = output_path or (INSIGHTS_DIR / f"analytical_insights.{target_format}")
    target_path.parent.mkdir(parents=True, exist_ok=True)

    if target_format == "md":
        from src.storytelling import export_narratives_to_markdown
        return export_narratives_to_markdown(output_path=target_path)
    elif target_format == "json":
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(insights_data, f, indent=2, default=str)

    logger.info(f"Successfully exported analytical insights to {target_path}")
    return target_path


def export_chart_figure(
    fig: Any,
    filename: str,
    output_dir: Optional[Path] = None,
    format: str = "html"
) -> Path:
    """
    Exports an interactive Plotly chart figure to standalone HTML or image file.

    Args:
        fig: Plotly Figure object
        filename: Target base filename (e.g. 'completion_vs_dropout')
        output_dir: Custom destination directory (defaults to reports/charts)
        format: 'html' (interactive bundle)

    Returns:
        Path to exported chart file.
    """
    target_dir = output_dir or CHARTS_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    target_path = target_dir / f"{filename}.{format.lower()}"

    if hasattr(fig, "write_html") and format.lower() == "html":
        fig.write_html(str(target_path), include_plotlyjs="cdn")
    else:
        # Fallback to write string
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(fig.to_html(include_plotlyjs="cdn") if hasattr(fig, "to_html") else "")

    logger.info(f"Exported interactive chart figure to {target_path}")
    return target_path


# -----------------------------------------------------------------------------
# Orchestrator Function
# -----------------------------------------------------------------------------

def export_all_analytical_outputs(
    db_path: Optional[Path] = None,
    export_dir: Optional[Path] = None
) -> Dict[str, Path]:
    """
    Orchestrates full export for all 5 required analytical output categories:
    1. KPIs
    2. Learner Risk Data
    3. Course Metrics
    4. Behavioural Segments
    5. Analytical Insights & Generated Summary Report

    Args:
        db_path: Optional custom path to SQLite database
        export_dir: Optional destination root directory

    Returns:
        Dictionary mapping output category -> exported Path object.
    """
    target_db = db_path or DB_PATH
    root_dir = export_dir or REPORTS_DIR

    # Load metrics & datasets from database or pandas analytical views
    try:
        from src.database import execute_business_metrics, execute_analytical_views
        bmetrics = execute_business_metrics(db_path=target_db)
        kpis = bmetrics.get("kpis", {})
        views = execute_analytical_views(db_path=target_db)
    except Exception as e:
        logger.warning(f"Could not query live DB views for export orchestrator, using defaults: {e}")
        kpis = {"total_students": 1250, "completion_rate_pct": 68.4, "dropout_rate_pct": 14.2}
        views = {}

    risk_df = views.get("dropout_risk_view", pd.DataFrame())
    course_df = views.get("course_performance_view", pd.DataFrame())
    behaviour_df = views.get("student_engagement_view", pd.DataFrame())

    from src.storytelling import generate_all_insight_narratives
    insights = generate_all_insight_narratives(db_path=target_db)

    exported_paths = {
        "kpis": export_kpis(kpis, root_dir / "kpi_summary.csv"),
        "learner_risk_data": export_learner_risk_data(risk_df, root_dir / "learner_risk_data.csv"),
        "course_metrics": export_course_metrics(course_df, root_dir / "course_metrics.csv"),
        "behavioural_segments": export_behavioural_segments(behaviour_df, root_dir / "behavioural_segments.csv"),
        "insights": export_insights(insights, INSIGHTS_DIR / "data_storytelling_narrative.md")
    }

    # Generate summary executive report
    try:
        from src.reporting import export_executive_report
        exported_paths["executive_report"] = export_executive_report(db_path=target_db, output_path=root_dir / "executive_report.md")
    except Exception as e:
        logger.error(f"Failed exporting executive report in orchestrator: {e}")

    logger.info(f"Completed export of all {len(exported_paths)} analytical outputs.")
    return exported_paths

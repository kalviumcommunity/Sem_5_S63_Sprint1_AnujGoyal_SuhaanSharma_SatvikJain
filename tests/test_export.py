"""
Unit tests for Concept #40: Insight Export & Report Generation Engine.
"""

import pytest
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
from src.export import (
    get_dataframe_csv_bytes,
    get_markdown_report_bytes,
    get_json_bytes,
    get_chart_html_bytes,
    export_kpis,
    export_learner_risk_data,
    export_course_metrics,
    export_behavioural_segments,
    export_insights,
    export_chart_figure,
    export_all_analytical_outputs,
)
from src.analysis import run_insight_export_analysis


def test_in_memory_byte_buffers():
    """Verify Streamlit download helper buffer generators."""
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    csv_bytes = get_dataframe_csv_bytes(df)
    assert isinstance(csv_bytes, bytes)
    assert b"a,b" in csv_bytes

    md_bytes = get_markdown_report_bytes("# Executive Report")
    assert isinstance(md_bytes, bytes)
    assert b"# Executive Report" in md_bytes

    json_bytes = get_json_bytes({"kpi": 100})
    assert isinstance(json_bytes, bytes)
    assert b'"kpi": 100' in json_bytes

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[1, 2], y=[3, 4]))
    html_bytes = get_chart_html_bytes(fig)
    assert isinstance(html_bytes, bytes)
    assert b"plotly" in html_bytes.lower()


def test_export_kpis(tmp_path):
    """Verify exporting KPIs to CSV and JSON formats."""
    kpis = {"total_students": 1000, "completion_rate_pct": 75.0}

    csv_path = export_kpis(kpis, output_path=tmp_path / "kpis.csv", format="csv")
    assert csv_path.exists()

    json_path = export_kpis(kpis, output_path=tmp_path / "kpis.json", format="json")
    assert json_path.exists()


def test_export_learner_risk_data(tmp_path):
    """Verify exporting learner risk data."""
    df = pd.DataFrame({
        "student_id": ["S001", "S002"],
        "dropout_risk_level": ["Low", "High"]
    })
    path = export_learner_risk_data(df, output_path=tmp_path / "risk.csv", format="csv")
    assert path.exists()
    assert "S001" in path.read_text(encoding="utf-8")


def test_export_course_metrics(tmp_path):
    """Verify exporting course metrics."""
    df = pd.DataFrame({
        "course_id": ["C001"],
        "course_title": ["Python"],
        "completion_rate_pct": [80.0]
    })
    path = export_course_metrics(df, output_path=tmp_path / "course.csv", format="csv")
    assert path.exists()


def test_export_behavioural_segments(tmp_path):
    """Verify exporting behavioural segments dataset."""
    df = pd.DataFrame({
        "student_id": ["S001"],
        "segment": ["High Engagement"],
        "sessions_per_week": [4.5]
    })
    path = export_behavioural_segments(df, output_path=tmp_path / "segments.csv", format="csv")
    assert path.exists()


def test_export_insights(tmp_path):
    """Verify exporting analytical insights report to markdown."""
    insights = {"domain": "completion", "title": "Test Insight"}
    path = export_insights(insights, output_path=tmp_path / "insights.md", format="md")
    assert path.exists()


def test_export_chart_figure(tmp_path):
    """Verify exporting Plotly chart figure to standalone interactive HTML."""
    fig = go.Figure()
    fig.add_trace(go.Bar(x=["A", "B"], y=[10, 20]))

    chart_path = export_chart_figure(fig, filename="completion_chart", output_dir=tmp_path, format="html")
    assert chart_path.exists()
    assert "plotly" in chart_path.read_text(encoding="utf-8").lower()


def test_export_all_analytical_outputs(tmp_path):
    """Verify orchestrator export function exports all 5 required outputs."""
    paths = export_all_analytical_outputs(export_dir=tmp_path)
    assert isinstance(paths, dict)
    assert "kpis" in paths
    assert "learner_risk_data" in paths
    assert "course_metrics" in paths
    assert "behavioural_segments" in paths
    assert "insights" in paths

    for key, path_obj in paths.items():
        assert path_obj.exists(), f"Exported file for '{key}' does not exist: {path_obj}"


def test_run_insight_export_analysis_wrapper(tmp_path):
    """Verify src.analysis wrapper executes insight export analysis cleanly."""
    res = run_insight_export_analysis(export_dir=tmp_path)
    assert isinstance(res, dict)
    assert "kpis" in res

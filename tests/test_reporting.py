"""
Unit tests for Concept #39: Executive Reporting & Stakeholder Communication.
"""

import pytest
from pathlib import Path
from src.reporting import (
    generate_executive_report_data,
    build_executive_report_markdown,
    export_executive_report,
)
from src.analysis import run_executive_reporting_analysis


def test_generate_executive_report_data_sections():
    """Verify report data contains all 8 required executive sections."""
    data = generate_executive_report_data()
    assert isinstance(data, dict)

    required_sections = [
        "overall_performance",
        "completion_analysis",
        "dropout_analysis",
        "learner_engagement",
        "major_behavioural_findings",
        "high_risk_segments",
        "course_level_findings",
        "recommended_actions"
    ]
    for section in required_sections:
        assert section in data, f"Missing required section '{section}' in report data"
        assert "title" in data[section]


def test_non_technical_clarity():
    """Verify executive report avoids technical code jargon and provides stakeholder-friendly summaries."""
    data = generate_executive_report_data()

    # Check overall performance section
    op = data["overall_performance"]
    assert len(op["kpi_cards"]) >= 5
    assert len(op["summary"]) > 20

    # Verify absence of raw technical variable names in titles
    for key, section_data in data.items():
        if key == "metadata":
            continue
        title = section_data.get("title", "")
        assert "_" not in title or "course_level" in key or "high_risk" in key


def test_build_executive_report_markdown():
    """Verify building formatted Markdown document from report data."""
    data = generate_executive_report_data()
    md = build_executive_report_markdown(data)

    assert isinstance(md, str)
    assert "# 📊 Executive Learning Analytics & Course Completion Report" in md
    assert "## 1. Overall Platform Performance" in md
    assert "## 2. Course Completion Analysis" in md
    assert "## 3. Learner Dropout Analysis" in md
    assert "## 4. Learner Engagement Dynamics" in md
    assert "## 5. Major Behavioural Findings" in md
    assert "## 6. High-Risk Learner Segments" in md
    assert "## 7. Course-Level Findings & Rankings" in md
    assert "## 8. Prioritized Strategic Recommendations" in md


def test_export_executive_report(tmp_path):
    """Verify exporting executive report to disk."""
    target_file = tmp_path / "executive_report.md"
    result_path = export_executive_report(output_path=target_file)

    assert result_path.exists()
    content = result_path.read_text(encoding="utf-8")
    assert "Executive Learning Analytics" in content
    assert "Prioritized Strategic Recommendations" in content


def test_run_executive_reporting_analysis_wrapper():
    """Verify src.analysis wrapper executes executive reporting cleanly."""
    res = run_executive_reporting_analysis()
    assert isinstance(res, dict)
    assert "overall_performance" in res
    assert "recommended_actions" in res

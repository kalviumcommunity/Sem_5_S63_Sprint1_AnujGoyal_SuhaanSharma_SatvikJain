"""
Unit tests for Concept #38: Data Storytelling & Insight Narrative Engine.
"""

import pytest
from pathlib import Path
from src.storytelling import (
    InsightNarrative,
    generate_engagement_narrative,
    generate_completion_narrative,
    generate_dropout_narrative,
    generate_risk_narrative,
    generate_course_performance_narrative,
    generate_all_insight_narratives,
    export_narratives_to_markdown,
)
from src.analysis import run_data_storytelling_analysis


def test_insight_narrative_dataclass_methods():
    """Verify InsightNarrative to_dict and to_markdown methods."""
    narrative = InsightNarrative(
        domain="test_domain",
        title="Test Executive Headline Title",
        observation="Test observation metric finding.",
        interpretation="Test associative interpretation.",
        business_impact="Test operational business impact.",
        suggested_action="Test strategic intervention action."
    )
    d = narrative.to_dict()
    assert isinstance(d, dict)
    assert d["domain"] == "test_domain"
    assert d["title"] == "Test Executive Headline Title"

    md = narrative.to_markdown()
    assert "💡 Test Executive Headline Title" in md
    assert "🔍 Observation:" in md
    assert "🧠 Interpretation:" in md
    assert "📈 Business Impact:" in md
    assert "🎯 Suggested Action:" in md


@pytest.mark.parametrize("generator_fn, expected_domain", [
    (generate_engagement_narrative, "engagement"),
    (generate_completion_narrative, "completion"),
    (generate_dropout_narrative, "dropout"),
    (generate_risk_narrative, "risk"),
    (generate_course_performance_narrative, "course_performance")
])
def test_domain_narrative_generators(generator_fn, expected_domain):
    """Verify narrative generators for all 5 required domains enforce 4-stage framework."""
    narrative = generator_fn()
    assert isinstance(narrative, InsightNarrative)
    assert narrative.domain == expected_domain

    # Enforce 4-stage non-empty structure
    assert len(narrative.title.strip()) > 5
    assert len(narrative.observation.strip()) > 10
    assert len(narrative.interpretation.strip()) > 10
    assert len(narrative.business_impact.strip()) > 10
    assert len(narrative.suggested_action.strip()) > 10


def test_no_unsupported_causal_claims():
    """Verify narratives avoid unsupported causal claims by using correlational / associative language."""
    narratives = generate_all_insight_narratives()
    banned_words = ["definitely causes", "proved causality", "directly forces"]

    for domain, narrative in narratives.items():
        text = (narrative.observation + " " + narrative.interpretation).lower()
        for banned in banned_words:
            assert banned not in text, f"Found unsupported causal claim '{banned}' in domain '{domain}'"


def test_generate_all_insight_narratives():
    """Verify generating all 5 required domain narratives at once."""
    narratives = generate_all_insight_narratives()
    assert isinstance(narratives, dict)
    assert len(narratives) == 5

    required_domains = ["engagement", "completion", "dropout", "risk", "course_performance"]
    for dom in required_domains:
        assert dom in narratives
        assert isinstance(narratives[dom], InsightNarrative)


def test_export_narratives_to_markdown(tmp_path):
    """Verify exporting narrative report to Markdown file."""
    output_file = tmp_path / "test_storytelling.md"
    result_path = export_narratives_to_markdown(output_path=output_file)

    assert result_path.exists()
    content = result_path.read_text(encoding="utf-8")
    assert "# Data Storytelling & Analytical Insight Narratives" in content
    assert "Observation → Interpretation → Business Impact → Suggested Action" in content
    assert "💡" in content


def test_run_data_storytelling_analysis_wrapper():
    """Verify src.analysis wrapper executes data storytelling analysis cleanly."""
    res = run_data_storytelling_analysis()
    assert isinstance(res, dict)
    assert "engagement" in res
    assert "completion" in res

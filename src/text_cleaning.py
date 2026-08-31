"""
String Cleaning & Text Normalisation Module for Learning Analytics.
Provides robust text sanitisation, whitespace collapsing, casing normalization,
technical acronym preservation, and category label standardization.
"""

import re
from typing import Dict, Any, List, Optional, Union
import pandas as pd
from src.utils import setup_logger, timed_step

logger = setup_logger(__name__)

# Common Tech Acronyms to Preserve in Title Casing
TECH_ACRONYMS = {
    "ai": "AI",
    "ml": "ML",
    "sql": "SQL",
    "dbms": "DBMS",
    "aws": "AWS",
    "gcp": "GCP",
    "api": "API",
    "html": "HTML",
    "css": "CSS",
    "js": "JS",
    "ui": "UI",
    "ux": "UX",
    "nlp": "NLP",
    "ci": "CI",
    "cd": "CD",
    "etl": "ETL",
    "bi": "BI",
    "iot": "IoT",
    "qa": "QA"
}

# Small grammatical words to keep lowercase in titles (unless first word)
LOWERCASE_WORDS = {"and", "as", "at", "but", "by", "for", "in", "nor", "of", "on", "or", "so", "the", "to", "up", "yet", "via", "with"}

# Canonical Category Label Mapping
CATEGORY_CANONICAL_MAP: Dict[str, str] = {
    "data science": "Data Science",
    "data_science": "Data Science",
    "datascience": "Data Science",
    "ds": "Data Science",
    "data analytics": "Data Science",
    "ai & ml": "AI & Machine Learning",
    "ai/ml": "AI & Machine Learning",
    "ai & machine learning": "AI & Machine Learning",
    "machine learning": "AI & Machine Learning",
    "artificial intelligence": "AI & Machine Learning",
    "ai": "AI & Machine Learning",
    "ml": "AI & Machine Learning",
    "deep learning": "AI & Machine Learning",
    "web dev": "Web Development",
    "web development": "Web Development",
    "web_development": "Web Development",
    "web-dev": "Web Development",
    "frontend": "Web Development",
    "full stack": "Web Development",
    "fullstack": "Web Development",
    "cloud": "Cloud Computing",
    "cloud computing": "Cloud Computing",
    "cloud_computing": "Cloud Computing",
    "cloud-computing": "Cloud Computing",
    "devops": "Cloud Computing",
    "cyber security": "Cybersecurity",
    "cybersecurity": "Cybersecurity",
    "cyber_security": "Cybersecurity",
    "cyber-sec": "Cybersecurity",
    "infosec": "Cybersecurity",
    "security": "Cybersecurity"
}


def normalize_whitespace(text: Any) -> str:
    """
    Strips leading/trailing whitespace, replaces tabs/newlines/non-breaking spaces,
    and collapses multiple internal spaces into a single space.
    """
    if pd.isna(text) or text is None:
        return ""
    
    val_str = str(text)
    # Replace non-breaking spaces and invisible Unicode whitespace with regular space
    val_str = re.sub(r"[\t\r\n\xa0\u2000-\u200b\u3000]", " ", val_str)
    # Collapse multiple spaces into one and trim edges
    val_str = re.sub(r"\s+", " ", val_str).strip()
    return val_str


def _format_word_token(word: str, is_first: bool = False) -> str:
    """Formats an individual word or compound token with punctuation and acronym preservation."""
    if not word:
        return ""
    
    # Leading punctuation/brackets
    i = 0
    while i < len(word) and word[i] in "([{<\"'":
        i += 1
    prefix = word[:i]

    # Trailing punctuation/brackets
    j = len(word)
    while j > i and word[j - 1] in ")]}>\"'.,:;!?":
        j -= 1
    suffix = word[j:]
    core = word[i:j]

    if not core:
        return word

    lower_core = core.lower()

    # Check direct acronym
    if lower_core in TECH_ACRONYMS:
        return f"{prefix}{TECH_ACRONYMS[lower_core]}{suffix}"

    # Handle compound sub-tokens split by / or -
    if "/" in core or "-" in core:
        sub_tokens = re.split(r"([/\-])", core)
        formatted_subs = []
        for st in sub_tokens:
            st_lower = st.lower()
            if st in {"/", "-"}:
                formatted_subs.append(st)
            elif st_lower in TECH_ACRONYMS:
                formatted_subs.append(TECH_ACRONYMS[st_lower])
            else:
                formatted_subs.append(st.capitalize())
        return f"{prefix}{''.join(formatted_subs)}{suffix}"

    # Grammatical lowercase check
    if not is_first and lower_core in LOWERCASE_WORDS:
        return f"{prefix}{lower_core}{suffix}"

    return f"{prefix}{core.capitalize()}{suffix}"


def clean_text_string(text: Any, casing: str = "title") -> Optional[str]:
    """
    Sanitizes raw text string with whitespace normalization and controlled casing.
    """
    if pd.isna(text) or text is None or text == "":
        return None

    cleaned = normalize_whitespace(text)
    if not cleaned:
        return ""

    if casing == "title":
        words = cleaned.split(" ")
        formatted = [_format_word_token(word, is_first=(i == 0)) for i, word in enumerate(words)]
        return " ".join(formatted)

    elif casing == "upper":
        return cleaned.upper()
    elif casing == "lower":
        return cleaned.lower()
    return cleaned


def clean_course_title(title: Any) -> str:
    """
    Normalizes course catalog titles preserving technical acronyms and proper title grammar.
    """
    if pd.isna(title) or title is None:
        return "Untitled Course"
    
    cleaned = clean_text_string(title, casing="title")
    return cleaned or "Untitled Course"


def clean_category_label(category: Any) -> str:
    """
    Normalizes academic/technical subject vertical labels against canonical domains.
    """
    if pd.isna(category) or category is None:
        return "General"

    raw_clean = normalize_whitespace(category).lower()
    if raw_clean in CATEGORY_CANONICAL_MAP:
        return CATEGORY_CANONICAL_MAP[raw_clean]
    
    # Fallback title casing for unmapped categories
    return clean_text_string(category, casing="title") or "General"


@timed_step("Clean DataFrame Text Fields")
def clean_text_dataframe(
    df: pd.DataFrame,
    entity_name: Optional[str] = None
) -> pd.DataFrame:
    """
    Applies comprehensive text and string cleaning across all textual columns in a DataFrame.
    """
    if df is None or df.empty:
        return pd.DataFrame() if df is None else df

    cleaned = df.copy()
    ent = entity_name.lower().strip() if entity_name else ""

    # 1. Clean all object/string columns by collapsing whitespace
    str_cols = cleaned.select_dtypes(include=["object", "string"]).columns
    for col in str_cols:
        cleaned[col] = cleaned[col].apply(lambda x: normalize_whitespace(x) if pd.notna(x) else x)

    # 2. Entity-specific string transformations
    if ent == "courses":
        if "course_title" in cleaned.columns:
            cleaned["course_title"] = cleaned["course_title"].apply(clean_course_title)
        if "category" in cleaned.columns:
            cleaned["category"] = cleaned["category"].apply(clean_category_label)

    elif ent == "students":
        if "education_level" in cleaned.columns:
            cleaned["education_level"] = cleaned["education_level"].apply(lambda x: clean_text_string(x, casing="title"))
        if "device_type" in cleaned.columns:
            cleaned["device_type"] = cleaned["device_type"].apply(lambda x: clean_text_string(x, casing="title"))

    logger.info(f"Standardized string text fields across '{entity_name or 'dataset'}'")
    return cleaned

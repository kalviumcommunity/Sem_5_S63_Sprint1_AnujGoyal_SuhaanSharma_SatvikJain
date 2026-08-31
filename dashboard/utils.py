"""
Dashboard Utility Helpers.
"""

from typing import Dict, Any
import pandas as pd


def format_metric(value: float, prefix: str = "", suffix: str = "") -> str:
    """Formats numeric values for dashboard KPI cards."""
    return f"{prefix}{value:,.1f}{suffix}"

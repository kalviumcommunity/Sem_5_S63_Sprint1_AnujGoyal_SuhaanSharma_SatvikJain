"""Periodic insight summaries and optional environment-backed email delivery."""

import os
import smtplib
from dataclasses import dataclass
from email.message import EmailMessage
from typing import Any, Dict, List, Optional, Protocol

import pandas as pd

from dashboard.alerts import MetricAlert, overall_alert_status


@dataclass(frozen=True)
class PeriodicSummary:
    """Concise stakeholder-ready learning analytics summary."""

    subject: str
    markdown: str
    plain_text: str


@dataclass(frozen=True)
class DeliveryResult:
    """Outcome of an optional report delivery attempt."""

    status: str
    message: str


class EmailService(Protocol):
    """Provider-independent contract for report delivery adapters."""

    def send(self, recipient: str, summary: PeriodicSummary) -> DeliveryResult:
        ...


# Keep the original name available to existing dashboard integrations.
EmailSender = EmailService


def _format_kpi_lines(kpis: Dict[str, Any]) -> List[str]:
    return [
        f"- Completion rate: {float(kpis.get('completion_rate_pct', 0.0) or 0.0):.1f}%",
        f"- Dropout rate: {float(kpis.get('dropout_rate_pct', 0.0) or 0.0):.1f}%",
        f"- Active learners: {int(kpis.get('active_learner_count', 0) or 0):,}",
        f"- At-risk learners: {int(kpis.get('at_risk_learner_count', 0) or 0):,}",
        f"- Average quiz score: {float(kpis.get('avg_quiz_score_pct', 0.0) or 0.0):.1f}%",
        f"- Average session duration: {float(kpis.get('avg_session_duration_minutes', 0.0) or 0.0):.1f} minutes",
    ]


def _trend_lines(views: Dict[str, pd.DataFrame]) -> List[str]:
    course_data = views.get("course_performance_view", pd.DataFrame())
    if course_data.empty or "completion_rate_pct" not in course_data.columns:
        return ["- No course-level trend is available for the selected period."]

    title_column = next((column for column in ["course_title", "course_id"] if column in course_data.columns), None)
    if title_column is None:
        return ["- Course trend data is unavailable for the selected period."]
    ordered = course_data.sort_values("completion_rate_pct", ascending=False)
    top = ordered.iloc[0]
    bottom = ordered.iloc[-1]
    return [
        f"- Strongest course completion: {top[title_column]} ({float(top['completion_rate_pct']):.1f}%).",
        f"- Lowest course completion: {bottom[title_column]} ({float(bottom['completion_rate_pct']):.1f}%).",
    ]


def _insight_lines(
    kpis: Dict[str, Any],
    views: Dict[str, pd.DataFrame],
    report_data: Optional[Dict[str, Any]] = None,
) -> List[str]:
    """Build concise analytical insights from the existing report inputs."""
    lines = [
        f"- Overall monitoring status is derived from current KPI and alert data.",
        f"- {int(kpis.get('at_risk_learner_count', 0) or 0):,} learners are currently in the high or critical risk population.",
    ]
    weekly = views.get("weekly_activity_view", pd.DataFrame())
    if not weekly.empty and "active_learners" in weekly.columns:
        active = pd.to_numeric(weekly["active_learners"], errors="coerce").dropna()
        if not active.empty:
            lines.append(f"- The latest weekly activity view contains {int(active.iloc[-1]):,} active learners.")
    for finding in (report_data or {}).get("major_behavioural_findings", {}).get("findings", [])[:3]:
        lines.append(f"- {finding.get('finding', 'Behavioural trend')}: {finding.get('detail', '')}")
    for section in ["completion_analysis", "dropout_analysis", "learner_engagement"]:
        takeaway = (report_data or {}).get(section, {}).get("key_takeaway")
        if takeaway:
            lines.append(f"- Analytical insight: {takeaway}")
    return lines


def build_periodic_summary(
    kpis: Dict[str, Any],
    views: Dict[str, pd.DataFrame],
    alerts: List[MetricAlert],
    period_label: str = "Current filtered period",
    report_data: Optional[Dict[str, Any]] = None,
) -> PeriodicSummary:
    """Build a concise summary from live KPIs, trends, alerts, and insights."""
    alert_lines = [
        f"- {alert.status}: {alert.metric} - {alert.explanation}"
        for alert in alerts
        if alert.status != "NORMAL"
    ]
    if not alert_lines:
        alert_lines = ["- No warning or critical metric alerts are active."]

    insight_lines = _insight_lines(kpis, views, report_data=report_data)
    insight_lines.insert(0, f"- Overall monitoring status is {overall_alert_status(alerts)}.")
    sections = [
        f"# Learning Analytics Summary: {period_label}",
        "",
        "## Key KPIs",
        *_format_kpi_lines(kpis),
        "",
        "## Major Trends",
        *_trend_lines(views),
        "",
        "## Risk Alerts",
        *alert_lines,
        "",
        "## Important Insights",
        *insight_lines,
    ]
    markdown = "\n".join(sections)
    plain_text = markdown.replace("# ", "").replace("## ", "")
    return PeriodicSummary(
        subject=f"Learning analytics summary - {period_label}",
        markdown=markdown,
        plain_text=plain_text,
    )


class SmtpEmailService:
    """SMTP implementation configured exclusively through environment variables."""

    def __init__(self, environ: Optional[Dict[str, str]] = None) -> None:
        self.environ = environ or os.environ

    def _configuration(self) -> Optional[Dict[str, Any]]:
        host = self.environ.get("LEARNING_ANALYTICS_SMTP_HOST")
        username = self.environ.get("LEARNING_ANALYTICS_SMTP_USERNAME")
        password = self.environ.get("LEARNING_ANALYTICS_SMTP_PASSWORD")
        sender = self.environ.get("LEARNING_ANALYTICS_REPORT_FROM")
        if not all([host, username, password, sender]):
            return None
        try:
            port = int(self.environ.get("LEARNING_ANALYTICS_SMTP_PORT", "587"))
        except ValueError:
            return None
        return {
            "host": host,
            "port": port,
            "username": username,
            "password": password,
            "sender": sender,
            "use_tls": self.environ.get("LEARNING_ANALYTICS_SMTP_USE_TLS", "true").lower() == "true",
        }

    def send(self, recipient: str, summary: PeriodicSummary) -> DeliveryResult:
        configuration = self._configuration()
        if configuration is None:
            return DeliveryResult(
                "NOT_CONFIGURED",
                "Email delivery is unavailable. Set the SMTP environment variables to enable it.",
            )
        if not recipient.strip():
            return DeliveryResult("INVALID_RECIPIENT", "Enter a recipient email address before sending.")

        message = EmailMessage()
        message["Subject"] = summary.subject
        message["From"] = configuration["sender"]
        message["To"] = recipient.strip()
        message.set_content(summary.plain_text)
        message.add_alternative(summary.markdown, subtype="markdown")

        try:
            with smtplib.SMTP(configuration["host"], configuration["port"], timeout=15) as smtp:
                if configuration["use_tls"]:
                    smtp.starttls()
                smtp.login(configuration["username"], configuration["password"])
                smtp.send_message(message)
        except (OSError, smtplib.SMTPException) as error:
            return DeliveryResult("FAILED", f"Email delivery failed: {error}")
        return DeliveryResult("SENT", "The learning analytics summary was sent successfully.")


class SmtpEmailSender(SmtpEmailService):
    """Backward-compatible name for the SMTP email service."""


class MockEmailService:
    """In-memory email adapter for tests and local UI demonstrations."""

    def __init__(self) -> None:
        self.sent_messages: List[Dict[str, str]] = []

    def send(self, recipient: str, summary: PeriodicSummary) -> DeliveryResult:
        if not recipient.strip():
            return DeliveryResult("INVALID_RECIPIENT", "Enter a recipient email address before sending.")
        self.sent_messages.append({
            "recipient": recipient.strip(),
            "subject": summary.subject,
            "plain_text": summary.plain_text,
            "markdown": summary.markdown,
        })
        return DeliveryResult("SENT", "The learning analytics summary was accepted by the mock email service.")


def get_email_sender(environ: Optional[Dict[str, str]] = None) -> EmailService:
    """Build the configured email provider without exposing credentials to the UI."""
    return SmtpEmailService(environ=environ)
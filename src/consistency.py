"""
Business Data Consistency & Validation Rules Module for Learning Analytics.
Enforces domain business rules (score ranges, positive durations, approved statuses,
valid identifiers, logical date boundaries, and registration-before-activity constraints)
with full audit documentation without silent modifications.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple, Union
import numpy as np
import pandas as pd
from src.utils import setup_logger, timed_step

logger = setup_logger(__name__)

# Approved Categorical Values
APPROVED_COMPLETION_STATUSES = {"Completed", "In Progress", "Dropped", "Inactive", "Unknown"}
APPROVED_GENDERS = {"Male", "Female", "Non-Binary", "Other", "Prefer not to say", "Unknown"}
APPROVED_EDUCATION_LEVELS = {"High School", "Undergraduate", "Postgraduate", "Doctorate", "Other", "Unknown"}
APPROVED_DEVICE_TYPES = {"Desktop", "Laptop", "Tablet", "Mobile", "Unknown"}


@dataclass
class RuleViolation:
    """Represents a specific business consistency rule violation."""
    rule_name: str
    entity_name: str
    row_index: Any
    record_id: Optional[str]
    field_name: str
    invalid_value: Any
    reason: str
    action_taken: str = "Tagged for Audit"

    def to_dict(self) -> Dict[str, Any]:
        """Converts violation to dictionary."""
        return {
            "Rule": self.rule_name,
            "Entity": self.entity_name,
            "Row Index": self.row_index,
            "Record ID": str(self.record_id) if self.record_id is not None else "N/A",
            "Field": self.field_name,
            "Invalid Value": str(self.invalid_value),
            "Violation Reason": self.reason,
            "Action Taken": self.action_taken
        }


@dataclass
class ConsistencyReport:
    """Comprehensive dataset-level business consistency audit report."""
    dataset_name: str
    total_records: int
    valid_records: int
    invalid_records: int
    pass_rate_pct: float
    rule_summaries: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    violations: List[RuleViolation] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Converts report to dictionary representation."""
        return {
            "dataset_name": self.dataset_name,
            "total_records": self.total_records,
            "valid_records": self.valid_records,
            "invalid_records": self.invalid_records,
            "pass_rate_pct": round(self.pass_rate_pct, 2),
            "rule_summaries": self.rule_summaries,
            "total_violations": len(self.violations)
        }

    def to_violations_df(self) -> pd.DataFrame:
        """Converts violations list to a tabular DataFrame for audit dashboards."""
        return pd.DataFrame([v.to_dict() for v in self.violations]) if self.violations else pd.DataFrame()

    def to_summary_df(self) -> pd.DataFrame:
        """Converts rule breakdown into a summary DataFrame."""
        rows = []
        for r_name, details in self.rule_summaries.items():
            rows.append({
                "Entity": self.dataset_name,
                "Business Rule": r_name,
                "Checked Count": details.get("checked_count", 0),
                "Violations Count": details.get("violations_count", 0),
                "Pass Rate %": f"{details.get('pass_rate', 100.0):.1f}%",
                "Status": "PASSED" if details.get("violations_count", 0) == 0 else "FLAGGED"
            })
        return pd.DataFrame(rows)


def _check_id_validity(val: Any) -> bool:
    """Checks that an ID is non-null, non-empty, and not a stringified placeholder."""
    if pd.isna(val) or val is None:
        return False
    s = str(val).strip().upper()
    if s in ("", "NAN", "NONE", "NULL", "UNKNOWN", "N/A", "UNDEFINED"):
        return False
    return len(s) >= 2


@timed_step("Validate Entity Business Rules")
def validate_entity_consistency(
    df: pd.DataFrame,
    entity_name: str,
    students_df: Optional[pd.DataFrame] = None
) -> Tuple[pd.DataFrame, ConsistencyReport]:
    """
    Validates domain business consistency rules for an entity and generates an audit log.
    """
    if df is None or df.empty:
        report = ConsistencyReport(
            dataset_name=entity_name,
            total_records=0,
            valid_records=0,
            invalid_records=0,
            pass_rate_pct=100.0
        )
        return pd.DataFrame() if df is None else df, report

    validated = df.copy()
    violations: List[RuleViolation] = []
    rule_counts: Dict[str, Dict[str, Any]] = {}
    ent = entity_name.lower().strip()

    # Track which rows have any violation
    violating_indices = set()

    # 1. Identifier Validation
    id_cols = [c for c in ["student_id", "course_id", "session_id", "quiz_attempt_id"] if c in validated.columns]
    for col in id_cols:
        r_name = f"Valid Identifier ({col})"
        v_cnt = 0
        for idx, val in validated[col].items():
            if not _check_id_validity(val):
                v_cnt += 1
                violating_indices.add(idx)
                violations.append(RuleViolation(
                    rule_name=r_name,
                    entity_name=entity_name,
                    row_index=idx,
                    record_id=str(val),
                    field_name=col,
                    invalid_value=val,
                    reason=f"Identifier '{col}' contains invalid/empty value",
                    action_taken="Flagged in Audit Report"
                ))
        rule_counts[r_name] = {
            "checked_count": len(validated),
            "violations_count": v_cnt,
            "pass_rate": round(((len(validated) - v_cnt) / len(validated) * 100.0), 2)
        }

    # 2. Entity Specific Rules
    if ent == "students":
        # Rule: Completion status approved values
        if "completion_status" in validated.columns:
            r_name = "Approved Completion Status"
            v_cnt = 0
            for idx, val in validated["completion_status"].items():
                if val not in APPROVED_COMPLETION_STATUSES:
                    v_cnt += 1
                    violating_indices.add(idx)
                    violations.append(RuleViolation(
                        rule_name=r_name,
                        entity_name=entity_name,
                        row_index=idx,
                        record_id=validated.at[idx, "student_id"] if "student_id" in validated.columns else idx,
                        field_name="completion_status",
                        invalid_value=val,
                        reason=f"Status '{val}' not in approved list: {APPROVED_COMPLETION_STATUSES}",
                        action_taken="Flagged in Audit Report"
                    ))
            rule_counts[r_name] = {
                "checked_count": len(validated),
                "violations_count": v_cnt,
                "pass_rate": round(((len(validated) - v_cnt) / len(validated) * 100.0), 2)
            }

        # Rule: Age between 15 and 90
        if "age" in validated.columns:
            r_name = "Valid Learner Age Range (15-90)"
            v_cnt = 0
            for idx, val in validated["age"].items():
                if pd.notna(val) and (val < 15 or val > 90):
                    v_cnt += 1
                    violating_indices.add(idx)
                    violations.append(RuleViolation(
                        rule_name=r_name,
                        entity_name=entity_name,
                        row_index=idx,
                        record_id=validated.at[idx, "student_id"] if "student_id" in validated.columns else idx,
                        field_name="age",
                        invalid_value=val,
                        reason=f"Age {val} is outside allowed range (15 to 90 years)",
                        action_taken="Flagged in Audit Report"
                    ))
            rule_counts[r_name] = {
                "checked_count": len(validated),
                "violations_count": v_cnt,
                "pass_rate": round(((len(validated) - v_cnt) / len(validated) * 100.0), 2)
            }

    elif ent == "sessions":
        # Rule: Session duration must be strictly positive
        if "duration_minutes" in validated.columns:
            r_name = "Positive Session Duration (> 0.0 mins)"
            v_cnt = 0
            for idx, val in validated["duration_minutes"].items():
                if pd.notna(val) and val <= 0.0:
                    v_cnt += 1
                    violating_indices.add(idx)
                    violations.append(RuleViolation(
                        rule_name=r_name,
                        entity_name=entity_name,
                        row_index=idx,
                        record_id=validated.at[idx, "session_id"] if "session_id" in validated.columns else idx,
                        field_name="duration_minutes",
                        invalid_value=val,
                        reason=f"Session duration {val}m must be strictly positive (>0)",
                        action_taken="Flagged in Audit Report"
                    ))
            rule_counts[r_name] = {
                "checked_count": len(validated),
                "violations_count": v_cnt,
                "pass_rate": round(((len(validated) - v_cnt) / len(validated) * 100.0), 2)
            }

        # Rule: session_start <= session_end
        if "session_start" in validated.columns and "session_end" in validated.columns:
            r_name = "Logical Session Timestamps (Start <= End)"
            v_cnt = 0
            start_dt = pd.to_datetime(validated["session_start"], errors="coerce")
            end_dt = pd.to_datetime(validated["session_end"], errors="coerce")
            for idx in validated.index:
                s_t = start_dt.loc[idx]
                e_t = end_dt.loc[idx]
                if pd.notna(s_t) and pd.notna(e_t) and s_t > e_t:
                    v_cnt += 1
                    violating_indices.add(idx)
                    violations.append(RuleViolation(
                        rule_name=r_name,
                        entity_name=entity_name,
                        row_index=idx,
                        record_id=validated.at[idx, "session_id"] if "session_id" in validated.columns else idx,
                        field_name="session_start / session_end",
                        invalid_value=f"Start: {s_t}, End: {e_t}",
                        reason="Session start timestamp occurs after session end timestamp",
                        action_taken="Flagged in Audit Report"
                    ))
            rule_counts[r_name] = {
                "checked_count": len(validated),
                "violations_count": v_cnt,
                "pass_rate": round(((len(validated) - v_cnt) / len(validated) * 100.0), 2)
            }

    elif ent == "quizzes":
        # Rule: Quiz score between 0 and 100
        if "score_percentage" in validated.columns:
            r_name = "Quiz Score Range (0.0 to 100.0%)"
            v_cnt = 0
            for idx, val in validated["score_percentage"].items():
                if pd.notna(val) and (val < 0.0 or val > 100.0):
                    v_cnt += 1
                    violating_indices.add(idx)
                    violations.append(RuleViolation(
                        rule_name=r_name,
                        entity_name=entity_name,
                        row_index=idx,
                        record_id=validated.at[idx, "quiz_attempt_id"] if "quiz_attempt_id" in validated.columns else idx,
                        field_name="score_percentage",
                        invalid_value=val,
                        reason=f"Score {val}% is outside valid range (0.0 to 100.0%)",
                        action_taken="Flagged in Audit Report"
                    ))
            rule_counts[r_name] = {
                "checked_count": len(validated),
                "violations_count": v_cnt,
                "pass_rate": round(((len(validated) - v_cnt) / len(validated) * 100.0), 2)
            }

    # Cross-Entity Rule: Registration date <= Activity date
    if students_df is not None and "student_id" in validated.columns and "registration_date" in students_df.columns:
        date_col = None
        if "session_start" in validated.columns:
            date_col = "session_start"
        elif "attempt_date" in validated.columns:
            date_col = "attempt_date"

        if date_col:
            r_name = "Enrollment Prior to Activity Date"
            v_cnt = 0
            # Build student reg lookup
            reg_lookup = students_df.set_index("student_id")["registration_date"].to_dict()
            act_dt = pd.to_datetime(validated[date_col], errors="coerce")
            
            for idx in validated.index:
                stu_id = validated.at[idx, "student_id"]
                if stu_id in reg_lookup:
                    reg_d = pd.to_datetime(reg_lookup[stu_id], errors="coerce")
                    act_d = act_dt.loc[idx]
                    if pd.notna(reg_d) and pd.notna(act_d) and reg_d.date() > act_d.date():
                        v_cnt += 1
                        violating_indices.add(idx)
                        violations.append(RuleViolation(
                            rule_name=r_name,
                            entity_name=entity_name,
                            row_index=idx,
                            record_id=stu_id,
                            field_name=date_col,
                            invalid_value=f"Reg: {reg_d.strftime('%Y-%m-%d')}, Activity: {act_d.strftime('%Y-%m-%d')}",
                            reason=f"Learning activity occurs before student enrollment date",
                            action_taken="Flagged in Audit Report"
                        ))
            rule_counts[r_name] = {
                "checked_count": len(validated),
                "violations_count": v_cnt,
                "pass_rate": round(((len(validated) - v_cnt) / len(validated) * 100.0), 2)
            }

    total_records = len(validated)
    invalid_records = len(violating_indices)
    valid_records = total_records - invalid_records
    pass_rate = (valid_records / total_records * 100.0) if total_records > 0 else 100.0

    report = ConsistencyReport(
        dataset_name=entity_name,
        total_records=total_records,
        valid_records=valid_records,
        invalid_records=invalid_records,
        pass_rate_pct=pass_rate,
        rule_summaries=rule_counts,
        violations=violations
    )

    logger.info(
        f"Validated business consistency for '{entity_name}': {valid_records}/{total_records} passed "
        f"({pass_rate:.1f}%), {len(violations)} rule violations flagged"
    )

    return validated, report


def validate_all_consistency(
    datasets: Dict[str, pd.DataFrame]
) -> Tuple[Dict[str, pd.DataFrame], Dict[str, ConsistencyReport]]:
    """
    Validates business rules across all project datasets with cross-entity checks.
    """
    students_df = datasets.get("students")
    validated_dict = {}
    reports_dict = {}

    for name, df in datasets.items():
        v_df, rep = validate_entity_consistency(
            df,
            entity_name=name,
            students_df=students_df if name != "students" else None
        )
        validated_dict[name] = v_df
        reports_dict[name] = rep

    return validated_dict, reports_dict


def generate_consistency_scorecard(
    reports: Dict[str, ConsistencyReport]
) -> pd.DataFrame:
    """
    Combines rule validation summaries across all entities into a consolidated scorecard.
    """
    dfs = [rep.to_summary_df() for rep in reports.values() if not rep.to_summary_df().empty]
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

"""
Data Dictionary & Business Context Mapping Module for Learning Analytics.
Provides programmatic metadata, business definitions, valid value domains,
and analytical applications for all columns across project entities.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
from pathlib import Path
from src.utils import setup_logger

logger = setup_logger(__name__)

DATA_DICTIONARY: Dict[str, Dict[str, Dict[str, Any]]] = {
    "students": {
        "student_id": {
            "data_type": "string",
            "business_meaning": "Unique alphanumeric identifier assigned to each registered learner.",
            "source_dataset": "students.csv / students.json",
            "valid_range": "Non-empty string (e.g., 'S001', 'STU_1042')",
            "required": True,
            "analysis_use": "Primary key for student-level aggregations, cohort tracking, and risk scoring."
        },
        "registration_date": {
            "data_type": "datetime (YYYY-MM-DD)",
            "business_meaning": "The calendar date when the student created their platform account and enrolled.",
            "source_dataset": "students.csv / students.json",
            "valid_range": "Historical date up to present (>= 2020-01-01)",
            "required": True,
            "analysis_use": "Cohort tenure calculation, registration seasonality analysis, and baseline onboarding timing."
        },
        "age": {
            "data_type": "integer",
            "business_meaning": "Age of the student in full years at time of registration.",
            "source_dataset": "students.csv / students.json",
            "valid_range": "15 to 80 years",
            "required": False,
            "analysis_use": "Demographic segmentation and completion likelihood by learner age bracket."
        },
        "gender": {
            "data_type": "string (categorical)",
            "business_meaning": "Self-reported gender identity of the learner.",
            "source_dataset": "students.csv / students.json",
            "valid_range": "['Male', 'Female', 'Non-Binary', 'Other', 'Prefer not to say']",
            "required": False,
            "analysis_use": "Equity and demographic engagement pattern comparisons."
        },
        "education_level": {
            "data_type": "string (categorical)",
            "business_meaning": "Highest formal education credential completed prior to enrollment.",
            "source_dataset": "students.csv / students.json",
            "valid_range": "['High School', 'Undergraduate', 'Postgraduate', 'Doctorate', 'Other']",
            "required": False,
            "analysis_use": "Learner background correlation with course difficulty and quiz performance."
        },
        "device_type": {
            "data_type": "string (categorical)",
            "business_meaning": "Primary device hardware used for accessing learning sessions.",
            "source_dataset": "students.csv / students.json",
            "valid_range": "['Desktop', 'Laptop', 'Tablet', 'Mobile']",
            "required": False,
            "analysis_use": "Platform accessibility analysis and engagement duration by hardware type."
        },
        "target_course_id": {
            "data_type": "string",
            "business_meaning": "Identifier of the primary course the student enrolled to complete.",
            "source_dataset": "students.csv / students.json",
            "valid_range": "Valid course_id matching courses entity (e.g., 'C101')",
            "required": True,
            "analysis_use": "Foreign key connecting student enrollment to course curriculum benchmarks."
        },
        "completion_status": {
            "data_type": "string (categorical)",
            "business_meaning": "Target business outcome: whether the student successfully completed or dropped.",
            "source_dataset": "students.csv / students.json",
            "valid_range": "['Completed', 'In Progress', 'Dropped', 'Inactive']",
            "required": True,
            "analysis_use": "Ground-truth target variable for dropout prediction and behavioral correlation models."
        }
    },
    "courses": {
        "course_id": {
            "data_type": "string",
            "business_meaning": "Unique course identifier in the catalog.",
            "source_dataset": "courses.csv / courses.json",
            "valid_range": "Non-empty string (e.g., 'C101', 'CRS_DATA_01')",
            "required": True,
            "analysis_use": "Primary key for course-level difficulty benchmarks and curriculum analytics."
        },
        "course_title": {
            "data_type": "string",
            "business_meaning": "Official marketing and catalog title of the course.",
            "source_dataset": "courses.csv / courses.json",
            "valid_range": "Descriptive string",
            "required": True,
            "analysis_use": "Dashboard labels, reporting filters, and course catalog categorization."
        },
        "category": {
            "data_type": "string (categorical)",
            "business_meaning": "Academic subject domain or technical skill vertical.",
            "source_dataset": "courses.csv / courses.json",
            "valid_range": "['Data Science', 'Web Development', 'AI & Machine Learning', 'Cloud Computing', 'Cybersecurity']",
            "required": True,
            "analysis_use": "Category-level completion benchmarking and cross-discipline engagement comparisons."
        },
        "total_modules": {
            "data_type": "integer",
            "business_meaning": "Total count of instructional curriculum modules required for graduation.",
            "source_dataset": "courses.csv / courses.json",
            "valid_range": "1 to 50 modules",
            "required": True,
            "analysis_use": "Denominator for calculating individual student percentage course progress."
        },
        "total_quizzes": {
            "data_type": "integer",
            "business_meaning": "Total number of graded milestone quizzes in the course.",
            "source_dataset": "courses.csv / courses.json",
            "valid_range": "1 to 20 quizzes",
            "required": True,
            "analysis_use": "Assessment completion rate tracking and milestone progress measurement."
        },
        "estimated_duration_hours": {
            "data_type": "float",
            "business_meaning": "Expected total learning hours needed to complete curriculum.",
            "source_dataset": "courses.csv / courses.json",
            "valid_range": "5.0 to 200.0 hours",
            "required": True,
            "analysis_use": "Pace calculation (actual hours vs. expected hours) to identify struggling learners."
        }
    },
    "sessions": {
        "session_id": {
            "data_type": "string",
            "business_meaning": "Unique event log identifier for each platform login session.",
            "source_dataset": "sessions.csv / sessions.json",
            "valid_range": "Non-empty string (e.g., 'SES_00912')",
            "required": True,
            "analysis_use": "Primary key for session event logs and activity sequence reconstruction."
        },
        "student_id": {
            "data_type": "string",
            "business_meaning": "Identifier of the student who initiated the study session.",
            "source_dataset": "sessions.csv / sessions.json",
            "valid_range": "Foreign key referencing students.student_id",
            "required": True,
            "analysis_use": "Aggregation key for total learning time, study frequency, and session regularity."
        },
        "course_id": {
            "data_type": "string",
            "business_meaning": "Identifier of the course accessed during the learning session.",
            "source_dataset": "sessions.csv / sessions.json",
            "valid_range": "Foreign key referencing courses.course_id",
            "required": True,
            "analysis_use": "Subject-specific time allocation and module focus tracking."
        },
        "session_start": {
            "data_type": "datetime (YYYY-MM-DD HH:MM:SS)",
            "business_meaning": "Exact timestamp when the student opened the learning session.",
            "source_dataset": "sessions.csv / sessions.json",
            "valid_range": "Valid timestamp <= session_end",
            "required": True,
            "analysis_use": "Time-of-day study habit analysis, inactivity gap calculation, and temporal drop-off detection."
        },
        "session_end": {
            "data_type": "datetime (YYYY-MM-DD HH:MM:SS)",
            "business_meaning": "Exact timestamp when the student closed or timed out of the session.",
            "source_dataset": "sessions.csv / sessions.json",
            "valid_range": "Valid timestamp >= session_start",
            "required": True,
            "analysis_use": "Total session duration calculation and session continuity checks."
        },
        "duration_minutes": {
            "data_type": "float",
            "business_meaning": "Total elapsed time in minutes from session start to session end.",
            "source_dataset": "sessions.csv / sessions.json",
            "valid_range": "0.1 to 600.0 minutes",
            "required": True,
            "analysis_use": "Gross learning engagement measure and study session length distribution."
        },
        "active_minutes": {
            "data_type": "float",
            "business_meaning": "Actual time in minutes spent actively typing, clicking, or playing video.",
            "source_dataset": "sessions.csv / sessions.json",
            "valid_range": "0.0 to duration_minutes",
            "required": True,
            "analysis_use": "Core engagement metric: distinguishing real study effort from passive open tabs."
        },
        "idle_minutes": {
            "data_type": "float",
            "business_meaning": "Time during the session with zero user interaction detected.",
            "source_dataset": "sessions.csv / sessions.json",
            "valid_range": "0.0 to duration_minutes",
            "required": True,
            "analysis_use": "Attention leakage indicator and distraction ratio calculation (idle / duration)."
        }
    },
    "quizzes": {
        "quiz_attempt_id": {
            "data_type": "string",
            "business_meaning": "Unique identifier for each individual quiz submission event.",
            "source_dataset": "quizzes.csv / quizzes.json",
            "valid_range": "Non-empty string (e.g., 'QA_5501')",
            "required": True,
            "analysis_use": "Primary key for assessment attempt logs and score history."
        },
        "student_id": {
            "data_type": "string",
            "business_meaning": "Identifier of the student attempting the quiz.",
            "source_dataset": "quizzes.csv / quizzes.json",
            "valid_range": "Foreign key referencing students.student_id",
            "required": True,
            "analysis_use": "Student assessment performance tracking and knowledge mastery aggregation."
        },
        "course_id": {
            "data_type": "string",
            "business_meaning": "Identifier of the course to which the quiz belongs.",
            "source_dataset": "quizzes.csv / quizzes.json",
            "valid_range": "Foreign key referencing courses.course_id",
            "required": True,
            "analysis_use": "Quiz difficulty comparisons across courses."
        },
        "quiz_id": {
            "data_type": "string",
            "business_meaning": "Identifier of the specific assessment module in the course.",
            "source_dataset": "quizzes.csv / quizzes.json",
            "valid_range": "Alphanumeric quiz code (e.g., 'QZ_MOD_01')",
            "required": True,
            "analysis_use": "Module-level bottleneck detection (identifying quizzes with unusually high failure rates)."
        },
        "attempt_number": {
            "data_type": "integer",
            "business_meaning": "Sequential retry counter for the student on this specific quiz.",
            "source_dataset": "quizzes.csv / quizzes.json",
            "valid_range": "1 to 10 attempts",
            "required": True,
            "analysis_use": "Struggle vs. persistence metric: retry behavior is a key behavioral predictor of completion."
        },
        "attempt_date": {
            "data_type": "datetime (YYYY-MM-DD)",
            "business_meaning": "Date when the quiz attempt was submitted.",
            "source_dataset": "quizzes.csv / quizzes.json",
            "valid_range": "Valid calendar date",
            "required": True,
            "analysis_use": "Pacing analysis and assessment milestone completion velocity."
        },
        "score_percentage": {
            "data_type": "float",
            "business_meaning": "Normalized assessment score achieved on a 0.0 to 100.0% scale.",
            "source_dataset": "quizzes.csv / quizzes.json",
            "valid_range": "0.0 to 100.0%",
            "required": True,
            "analysis_use": "Primary academic performance KPI and competency threshold verification."
        },
        "time_taken_minutes": {
            "data_type": "float",
            "business_meaning": "Minutes elapsed during the quiz attempt from start to submission.",
            "source_dataset": "quizzes.csv / quizzes.json",
            "valid_range": "1.0 to 180.0 minutes",
            "required": True,
            "analysis_use": "Guessing vs. mastery detection (abnormally fast times vs. normal completion)."
        },
        "passed": {
            "data_type": "integer (boolean flag)",
            "business_meaning": "Binary indicator whether score met or exceeded passing threshold (>=70%).",
            "source_dataset": "quizzes.csv / quizzes.json",
            "valid_range": "1 (Passed) or 0 (Failed)",
            "required": True,
            "analysis_use": "Milestone gatekeeper metric determining eligibility for course completion."
        }
    },
    "derived_metrics": {
        "session_date": {
            "data_type": "date (YYYY-MM-DD)",
            "business_meaning": "Calendar day of learning derived from session_start timestamp.",
            "source_dataset": "Derived from sessions.session_start",
            "valid_range": "Valid date",
            "required": True,
            "analysis_use": "Daily active users (DAU), day-of-week learning habits, and session gap tracking."
        },
        "session_duration": {
            "data_type": "float",
            "business_meaning": "Alias for duration_minutes representing total session length in minutes.",
            "source_dataset": "Derived from sessions",
            "valid_range": "0.1 to 600.0 minutes",
            "required": True,
            "analysis_use": "Study session volume and active learning depth measurement."
        },
        "quiz_score": {
            "data_type": "float",
            "business_meaning": "Alias for score_percentage representing quiz exam performance.",
            "source_dataset": "Derived from quizzes",
            "valid_range": "0.0 to 100.0%",
            "required": True,
            "analysis_use": "Knowledge retention assessment and academic strength scoring."
        },
        "progress_pct": {
            "data_type": "float",
            "business_meaning": "Percentage of total required course modules successfully completed (0-100%).",
            "source_dataset": "Calculated: (completed_modules / total_modules) * 100",
            "valid_range": "0.0% to 100.0%",
            "required": True,
            "analysis_use": "Linear progression indicator and early milestone dropout velocity tracking."
        }
    }
}


def get_data_dictionary_dataframe(entity_name: Optional[str] = None) -> pd.DataFrame:
    """
    Returns the data dictionary as a structured Pandas DataFrame.
    """
    records = []
    entities = [entity_name] if entity_name and entity_name in DATA_DICTIONARY else DATA_DICTIONARY.keys()

    for ent in entities:
        for col, meta in DATA_DICTIONARY[ent].items():
            records.append({
                "Entity / Dataset": ent,
                "Column Name": col,
                "Data Type": meta["data_type"],
                "Business Meaning": meta["business_meaning"],
                "Source Dataset": meta["source_dataset"],
                "Valid Range / Values": meta["valid_range"],
                "Required": "Yes" if meta["required"] else "No",
                "Analysis Application": meta["analysis_use"]
            })

    return pd.DataFrame(records)


def get_column_business_context(column_name: str, entity_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Retrieves the business definition and analytical purpose for a specific column.
    """
    col_clean = column_name.strip().lower()
    entities = [entity_name] if entity_name and entity_name in DATA_DICTIONARY else DATA_DICTIONARY.keys()

    for ent in entities:
        for col, meta in DATA_DICTIONARY[ent].items():
            if col.lower() == col_clean:
                return {
                    "entity": ent,
                    "column_name": col,
                    **meta
                }
    return None

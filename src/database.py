"""
Database Management Module for Learning Analytics.
Handles SQLite database connection, table initialization, and querying.
"""

from pathlib import Path
from typing import Optional
import sqlite3
import pandas as pd
from src.utils import DB_PATH, SQL_DIR, setup_logger, ensure_directories_exist

logger = setup_logger(__name__)


def get_db_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """Returns a connection to the SQLite database."""
    target_path = db_path or DB_PATH
    ensure_directories_exist()
    return sqlite3.connect(str(target_path))


def init_views(views_path: Optional[Path] = None, db_path: Optional[Path] = None) -> None:
    """Initializes reusable analytical SQL views using views.sql."""
    views_file = views_path or (SQL_DIR / "views.sql")
    if not views_file.exists():
        logger.warning(f"Views file not found at {views_file}")
        return

    with open(views_file, "r", encoding="utf-8") as f:
        views_sql = f.read()

    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.executescript(views_sql)
        conn.commit()
        logger.info("Database analytical views initialized successfully.")
    finally:
        conn.close()


def init_database(schema_path: Optional[Path] = None, db_path: Optional[Path] = None) -> None:
    """Initializes the database schema using schema.sql and creates views."""
    schema_file = schema_path or (SQL_DIR / "schema.sql")
    if not schema_file.exists():
        logger.warning(f"Schema file not found at {schema_file}")
        return
    
    with open(schema_file, "r", encoding="utf-8") as f:
        schema_sql = f.read()
        
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.executescript(schema_sql)
        conn.commit()
        logger.info("Database schema initialized successfully.")
    finally:
        conn.close()

    init_views(db_path=db_path)


def query_to_dataframe(query: str, db_path: Optional[Path] = None) -> pd.DataFrame:
    """Executes a SQL query and returns the results as a pandas DataFrame."""
    conn = get_db_connection(db_path)
    try:
        return pd.read_sql_query(query, conn)
    finally:
        conn.close()


def load_processed_data_to_sqlite(
    datasets: dict,
    db_path: Optional[Path] = None,
    if_exists: str = "replace"
) -> dict:
    """
    Loads a dictionary of processed DataFrames into SQLite tables.

    Args:
        datasets: Dictionary mapping table name -> pd.DataFrame
        db_path: Optional custom path to SQLite database file
        if_exists: Strategy for existing tables ('replace', 'append', 'fail')

    Returns:
        Dictionary mapping table_name -> inserted_row_count
    """
    from src.storage import save_to_database

    target_db = db_path or DB_PATH
    init_database(db_path=target_db)
    inserted_counts = {}

    for table_name, df in datasets.items():
        if df is not None and not df.empty:
            save_to_database(df, table_name, db_path=target_db, if_exists=if_exists)
            inserted_counts[table_name] = len(df)
            logger.info(f"Loaded {len(df)} rows into table '{table_name}'.")

    return inserted_counts


def validate_database_insertion(
    db_path: Optional[Path] = None,
    expected_tables: Optional[list] = None
) -> dict:
    """
    Validates that database tables exist and contain valid inserted data.

    Args:
        db_path: Path to SQLite database
        expected_tables: List of expected table names

    Returns:
        Dictionary containing validation status, table row counts, and error details
    """
    tables_to_check = expected_tables or ["students", "courses", "sessions", "quizzes", "behavioural_features"]
    conn = get_db_connection(db_path)
    report = {
        "status": "VALID",
        "existing_tables": [],
        "missing_tables": [],
        "table_row_counts": {},
        "errors": []
    }

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        db_tables = set(row[0] for row in cursor.fetchall())
        report["existing_tables"] = list(db_tables)

        for table in tables_to_check:
            if table in db_tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table};") # tbl name checked against schema list
                count = cursor.fetchone()[0]
                report["table_row_counts"][table] = count
            else:
                report["missing_tables"].append(table)
                report["errors"].append(f"Table '{table}' is missing from database.")
                report["status"] = "INVALID"

    except Exception as e:
        report["status"] = "ERROR"
        report["errors"].append(str(e))
    finally:
        conn.close()

    logger.info(f"Database validation complete. Status: {report['status']}")
    return report


def load_sql_queries_from_file(sql_file_path: Optional[Path] = None) -> dict:
    """
    Parses a SQL script file annotated with '-- Name: query_name' into a dictionary of named queries.

    Args:
        sql_file_path: Path to the SQL file (defaults to sql/business_metrics.sql)

    Returns:
        Dictionary mapping query_name -> sql_query_string
    """
    target_file = sql_file_path or (SQL_DIR / "business_metrics.sql")
    if not target_file.exists():
        logger.warning(f"SQL metrics query file not found at {target_file}")
        return {}

    with open(target_file, "r", encoding="utf-8") as f:
        content = f.read()

    queries = {}
    current_name = None
    current_lines = []

    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("-- Name:"):
            if current_name and current_lines:
                raw_sql = "\n".join(current_lines).strip()
                if ";" in raw_sql:
                    raw_sql = raw_sql[:raw_sql.rfind(";")+1].strip()
                queries[current_name] = raw_sql
                current_lines = []
            current_name = stripped.replace("-- Name:", "").strip()
        elif current_name:
            if stripped.startswith("--") and current_lines and any(";" in l for l in current_lines):
                continue
            current_lines.append(line)

    if current_name and current_lines:
        raw_sql = "\n".join(current_lines).strip()
        if ";" in raw_sql:
            raw_sql = raw_sql[:raw_sql.rfind(";")+1].strip()
        queries[current_name] = raw_sql

    logger.info(f"Loaded {len(queries)} named SQL queries from {target_file.name}")
    return queries


def execute_business_metrics(
    db_path: Optional[Path] = None,
    sql_file_path: Optional[Path] = None
) -> dict:
    """
    Executes core business metric queries from sql/business_metrics.sql against SQLite.

    Args:
        db_path: Path to SQLite database file
        sql_file_path: Custom path to business_metrics.sql

    Returns:
        Dictionary containing KPI metrics, executive summary DataFrame, and category breakdown DataFrame
    """
    queries = load_sql_queries_from_file(sql_file_path)
    target_db = db_path or DB_PATH

    results = {
        "kpis": {},
        "raw_results": {},
        "category_breakdown": pd.DataFrame()
    }

    for name, query_str in queries.items():
        if not query_str.endswith(";"):
            query_str += ";"
        try:
            df = query_to_dataframe(query_str, db_path=target_db)
            results["raw_results"][name] = df

            # Populate top-level KPI metrics dictionary if single-row result
            if name == "executive_kpi_overview" and not df.empty:
                row = df.iloc[0].to_dict()
                results["kpis"] = row
            elif name == "metrics_by_category":
                results["category_breakdown"] = df
            elif not df.empty and len(df) == 1:
                row_dict = df.iloc[0].to_dict()
                results["kpis"].update(row_dict)

        except Exception as e:
            logger.error(f"Failed executing SQL metric query '{name}': {e}")
            results["raw_results"][name] = pd.DataFrame()

    logger.info(f"Executed business metric queries successfully against database.")
    return results



def execute_multi_table_joins(

def execute_aggregation_queries(

    db_path: Optional[Path] = None,
    sql_file_path: Optional[Path] = None
) -> dict:
    """

    Executes multi-table INNER and LEFT JOIN queries from sql/multi_table_joins.sql against SQLite.

    Args:
        db_path: Path to SQLite database file
        sql_file_path: Custom path to multi_table_joins.sql

    Executes SQL filtering, grouping, and aggregation queries from sql/aggregation.sql against SQLite.

    Args:
        db_path: Path to SQLite database file
        sql_file_path: Custom path to aggregation.sql


    Returns:
        Dictionary mapping query_name -> pd.DataFrame
    """

    target_sql = sql_file_path or (SQL_DIR / "multi_table_joins.sql")

    target_sql = sql_file_path or (SQL_DIR / "aggregation.sql")

    queries = load_sql_queries_from_file(target_sql)
    target_db = db_path or DB_PATH

    results = {}
    for name, query_str in queries.items():
        if not query_str.endswith(";"):
            query_str += ";"
        try:
            df = query_to_dataframe(query_str, db_path=target_db)
            results[name] = df

            logger.info(f"Successfully executed multi-table join query '{name}' ({len(df)} rows returned).")
        except Exception as e:
            logger.error(f"Failed executing multi-table join query '{name}': {e}")

            logger.info(f"Successfully executed aggregation query '{name}' ({len(df)} rows returned).")
        except Exception as e:
            logger.error(f"Failed executing aggregation query '{name}': {e}")

            results[name] = pd.DataFrame()

    return results


def execute_window_function_queries(
    db_path: Optional[Path] = None,
    sql_file_path: Optional[Path] = None
) -> dict:
    """
    Executes SQL window function queries from sql/window_functions.sql against SQLite.

    Args:
        db_path: Path to SQLite database file
        sql_file_path: Custom path to window_functions.sql

    Returns:
        Dictionary mapping query_name -> pd.DataFrame
    """
    target_sql = sql_file_path or (SQL_DIR / "window_functions.sql")
    queries = load_sql_queries_from_file(target_sql)
    target_db = db_path or DB_PATH

    results = {}
    for name, query_str in queries.items():
        if not query_str.endswith(";"):
            query_str += ";"
        try:
            df = query_to_dataframe(query_str, db_path=target_db)
            results[name] = df
            logger.info(f"Successfully executed window function query '{name}' ({len(df)} rows returned).")
        except Exception as e:
            logger.error(f"Failed executing window function query '{name}': {e}")
            results[name] = pd.DataFrame()

    return results


def create_database_indexes(db_path: Optional[Path] = None) -> list:
    """
    Creates performance optimization indexes in SQLite database if they do not already exist.

    Args:
        db_path: Custom path to SQLite database

    Returns:
        List of index names created/verified.
    """
    index_statements = [
        "CREATE INDEX IF NOT EXISTS idx_students_target_course ON students(target_course_id);",
        "CREATE INDEX IF NOT EXISTS idx_students_reg_date ON students(registration_date);",
        "CREATE INDEX IF NOT EXISTS idx_sessions_student_start ON sessions(student_id, session_start);",
        "CREATE INDEX IF NOT EXISTS idx_sessions_course ON sessions(course_id);",
        "CREATE INDEX IF NOT EXISTS idx_quizzes_student_quiz ON quizzes(student_id, quiz_id, attempt_number);",
        "CREATE INDEX IF NOT EXISTS idx_quizzes_course ON quizzes(course_id);",
        "CREATE INDEX IF NOT EXISTS idx_behavioural_risk ON behavioural_features(dropout_risk_level);",
        "CREATE INDEX IF NOT EXISTS idx_behavioural_inactivity ON behavioural_features(days_since_last_activity);"
    ]
    conn = get_db_connection(db_path)
    created_indexes = []
    try:
        cursor = conn.cursor()
        for stmt in index_statements:
            cursor.execute(stmt)
            idx_name = stmt.split("IF NOT EXISTS ")[1].split(" ON")[0]
            created_indexes.append(idx_name)
        conn.commit()
        logger.info(f"Created/verified {len(created_indexes)} SQLite performance indexes.")
    finally:
        conn.close()
    return created_indexes


def explain_query_plan(query: str, db_path: Optional[Path] = None) -> pd.DataFrame:
    """
    Executes EXPLAIN QUERY PLAN for a given SQL query to analyze indexing and execution strategy.

    Args:
        query: SQL query string to profile
        db_path: Path to SQLite database

    Returns:
        DataFrame containing EXPLAIN QUERY PLAN output
    """
    explain_sql = f"EXPLAIN QUERY PLAN {query}"
    return query_to_dataframe(explain_sql, db_path=db_path)


def benchmark_query(query: str, db_path: Optional[Path] = None, runs: int = 10) -> dict:
    """
    Benchmarks query execution timing over multiple runs.

    Args:
        query: SQL query string to measure
        db_path: Path to SQLite database
        runs: Number of timing repetitions

    Returns:
        Dictionary containing timing metrics (avg_time_ms, min_time_ms, max_time_ms, runs)
    """
    import time
    conn = get_db_connection(db_path)
    timings = []
    try:
        for _ in range(runs):
            t0 = time.perf_counter()
            cursor = conn.cursor()
            cursor.execute(query)
            cursor.fetchall()
            t1 = time.perf_counter()
            timings.append((t1 - t0) * 1000.0)
    finally:
        conn.close()

    avg_ms = sum(timings) / len(timings) if timings else 0.0
    return {
        "avg_time_ms": round(avg_ms, 3),
        "min_time_ms": round(min(timings), 3) if timings else 0.0,
        "max_time_ms": round(max(timings), 3) if timings else 0.0,
        "runs": runs
    }


def execute_analytical_views(db_path: Optional[Path] = None) -> dict:
    """
    Queries all reusable analytical views from SQLite and returns a dictionary of DataFrames.

    Args:
        db_path: Custom path to SQLite database

    Returns:
        Dictionary mapping view_name -> pd.DataFrame
    """
    target_db = db_path or DB_PATH
    init_views(db_path=target_db)

    view_names = [
        "student_engagement_view",
        "course_performance_view",
        "dropout_risk_view",
        "weekly_activity_view"
    ]

    results = {}
    for vname in view_names:
        try:
            df = query_to_dataframe(f"SELECT * FROM {vname};", db_path=target_db)
            results[vname] = df
            logger.info(f"Successfully loaded analytical view '{vname}' ({len(df)} rows).")
        except Exception as e:
            logger.error(f"Failed loading analytical view '{vname}': {e}")
            results[vname] = pd.DataFrame()

    return results


def validate_views_against_pandas(
    db_path: Optional[Path] = None,
    datasets: Optional[dict] = None
) -> dict:
    """
    Validates each SQL view's calculations against pure Pandas calculations.

    Args:
        db_path: Path to SQLite database
        datasets: Dictionary of DataFrames (students, courses, sessions, quizzes, behavioural_features)

    Returns:
        Validation report dictionary with status, match metrics, and discrepancies.
    """
    target_db = db_path or DB_PATH
    sql_views = execute_analytical_views(db_path=target_db)

    report = {
        "status": "VALID",
        "views_checked": list(sql_views.keys()),
        "validation_details": {},
        "errors": []
    }

    try:
        if datasets is None:
            datasets = {
                "students": query_to_dataframe("SELECT * FROM students;", db_path=target_db),
                "courses": query_to_dataframe("SELECT * FROM courses;", db_path=target_db),
                "sessions": query_to_dataframe("SELECT * FROM sessions;", db_path=target_db),
                "quizzes": query_to_dataframe("SELECT * FROM quizzes;", db_path=target_db),
                "behavioural_features": query_to_dataframe("SELECT * FROM behavioural_features;", db_path=target_db)
            }

        students = datasets.get("students", pd.DataFrame())
        courses = datasets.get("courses", pd.DataFrame())
        sessions = datasets.get("sessions", pd.DataFrame())
        behavioural_features = datasets.get("behavioural_features", pd.DataFrame())

        # 1. Validate student_engagement_view
        se_view = sql_views.get("student_engagement_view", pd.DataFrame())
        if not students.empty:
            se_pandas_count = len(students)
            se_sql_count = len(se_view)
            se_match = (se_pandas_count == se_sql_count)
            report["validation_details"]["student_engagement_view"] = {
                "pandas_rows": se_pandas_count,
                "sql_rows": se_sql_count,
                "match": se_match
            }
            if not se_match:
                report["status"] = "INVALID"
                report["errors"].append(f"student_engagement_view row mismatch: Pandas={se_pandas_count}, SQL={se_sql_count}")

        # 2. Validate course_performance_view
        cp_view = sql_views.get("course_performance_view", pd.DataFrame())
        if not courses.empty:
            cp_pandas_count = len(courses)
            cp_sql_count = len(cp_view)
            cp_match = (cp_pandas_count == cp_sql_count)
            report["validation_details"]["course_performance_view"] = {
                "pandas_courses": cp_pandas_count,
                "sql_courses": cp_sql_count,
                "match": cp_match
            }
            if not cp_match:
                report["status"] = "INVALID"
                report["errors"].append(f"course_performance_view row mismatch: Pandas={cp_pandas_count}, SQL={cp_sql_count}")

        # 3. Validate dropout_risk_view
        dr_view = sql_views.get("dropout_risk_view", pd.DataFrame())
        if not behavioural_features.empty and not dr_view.empty:
            high_crit_pandas = len(behavioural_features[behavioural_features["dropout_risk_level"].str.lower().isin(["high", "critical"])])
            high_crit_sql = int(dr_view["is_at_risk"].sum())
            dr_match = (high_crit_pandas == high_crit_sql)
            report["validation_details"]["dropout_risk_view"] = {
                "pandas_at_risk": high_crit_pandas,
                "sql_at_risk": high_crit_sql,
                "match": dr_match
            }
            if not dr_match:
                report["status"] = "INVALID"
                report["errors"].append(f"dropout_risk_view at-risk count mismatch: Pandas={high_crit_pandas}, SQL={high_crit_sql}")

        # 4. Validate weekly_activity_view
        wa_view = sql_views.get("weekly_activity_view", pd.DataFrame())
        if not sessions.empty and "session_start" in sessions.columns and not wa_view.empty:
            valid_sessions = sessions[sessions["session_start"].notna() & (sessions["session_start"] != "")]
            tot_sess_pandas = len(valid_sessions)
            tot_sess_sql = int(wa_view["total_sessions"].sum())
            wa_match = (tot_sess_pandas == tot_sess_sql)
            report["validation_details"]["weekly_activity_view"] = {
                "pandas_total_sessions": tot_sess_pandas,
                "sql_total_sessions": tot_sess_sql,
                "match": wa_match
            }
            if not wa_match:
                report["status"] = "INVALID"
                report["errors"].append(f"weekly_activity_view total sessions mismatch: Pandas={tot_sess_pandas}, SQL={tot_sess_sql}")

    except Exception as e:
        report["status"] = "ERROR"
        report["errors"].append(str(e))

    logger.info(f"Views validation against Pandas complete. Status: {report['status']}")
    return report


def validate_sql_insights_against_pandas(
    db_path: Optional[Path] = None,
    datasets: Optional[dict] = None,
    tolerance: float = 1e-2
) -> dict:
    """
    Validates core SQL business metrics against equivalent Pandas DataFrame calculations.

    Metrics compared:
    - total_students
    - completion_rate_pct
    - dropout_rate_pct
    - active_learner_count
    - avg_quiz_score_pct
    - avg_session_duration_minutes
    - at_risk_learner_count

    Args:
        db_path: Path to SQLite database
        datasets: Dictionary mapping table name -> pd.DataFrame
        tolerance: Allowed floating-point absolute difference tolerance

    Returns:
        Validation report dictionary containing comparison table, status, and discrepancies.
    """
    target_db = db_path or DB_PATH
    sql_metrics = execute_business_metrics(db_path=target_db).get("kpis", {})

    if datasets is None:
        datasets = {
            "students": query_to_dataframe("SELECT * FROM students;", db_path=target_db),
            "sessions": query_to_dataframe("SELECT * FROM sessions;", db_path=target_db),
            "quizzes": query_to_dataframe("SELECT * FROM quizzes;", db_path=target_db),
            "behavioural_features": query_to_dataframe("SELECT * FROM behavioural_features;", db_path=target_db)
        }

    students = datasets.get("students", pd.DataFrame())
    sessions = datasets.get("sessions", pd.DataFrame())
    quizzes = datasets.get("quizzes", pd.DataFrame())
    behavioural_features = datasets.get("behavioural_features", pd.DataFrame())

    pandas_metrics = {}

    # 1. Total Students & Completion Rate %
    if not students.empty and "completion_status" in students.columns:
        tot_students = len(students)
        comp_count = (students["completion_status"].astype(str).str.lower() == "completed").sum()
        pandas_metrics["total_students"] = tot_students
        pandas_metrics["completion_rate_pct"] = round(100.0 * comp_count / max(tot_students, 1), 2)
    else:
        pandas_metrics["total_students"] = 0
        pandas_metrics["completion_rate_pct"] = 0.0

    # 2. Dropout Rate %
    if not students.empty and "completion_status" in students.columns:
        tot_students = len(students)
        drop_count = (students["completion_status"].astype(str).str.lower() == "dropped").sum()
        pandas_metrics["dropout_rate_pct"] = round(100.0 * drop_count / max(tot_students, 1), 2)
    else:
        pandas_metrics["dropout_rate_pct"] = 0.0

    # 3. Active Learner Count
    if not sessions.empty and "student_id" in sessions.columns:
        pandas_metrics["active_learner_count"] = int(sessions["student_id"].nunique())
    else:
        pandas_metrics["active_learner_count"] = 0

    # 4. Average Quiz Score %
    if not quizzes.empty and "score_percentage" in quizzes.columns:
        pandas_metrics["avg_quiz_score_pct"] = round(float(quizzes["score_percentage"].mean()), 2)
    else:
        pandas_metrics["avg_quiz_score_pct"] = 0.0

    # 5. Average Session Duration (minutes)
    if not sessions.empty and "duration_minutes" in sessions.columns:
        pandas_metrics["avg_session_duration_minutes"] = round(float(sessions["duration_minutes"].mean()), 2)
    else:
        pandas_metrics["avg_session_duration_minutes"] = 0.0

    # 6. At-Risk Learner Count
    if not behavioural_features.empty and "dropout_risk_level" in behavioural_features.columns:
        at_risk_mask = behavioural_features["dropout_risk_level"].astype(str).str.lower().isin(["high", "critical"])
        pandas_metrics["at_risk_learner_count"] = int(at_risk_mask.sum())
    else:
        pandas_metrics["at_risk_learner_count"] = 0

    comparison_results = {}
    is_valid = True
    discrepancies = []

    metrics_to_compare = [
        "total_students",
        "completion_rate_pct",
        "dropout_rate_pct",
        "active_learner_count",
        "avg_quiz_score_pct",
        "avg_session_duration_minutes",
        "at_risk_learner_count"
    ]

    for metric in metrics_to_compare:
        sql_val = sql_metrics.get(metric, 0.0)
        pd_val = pandas_metrics.get(metric, 0.0)
        delta = round(abs(float(sql_val) - float(pd_val)), 4)
        match = (delta <= tolerance)

        comparison_results[metric] = {
            "sql_value": sql_val,
            "pandas_value": pd_val,
            "absolute_difference": delta,
            "match": match
        }

        if not match:
            is_valid = False
            discrepancies.append(f"Metric '{metric}' mismatch: SQL={sql_val}, Pandas={pd_val} (delta={delta})")

    report = {
        "status": "VALID" if is_valid else "INVALID",
        "tolerance": tolerance,
        "metrics_compared": len(metrics_to_compare),
        "comparison_results": comparison_results,
        "discrepancies": discrepancies
    }

    logger.info(f"SQL vs Pandas insight validation complete. Status: {report['status']}")
    return report






def validate_join_expansion_integrity(db_path: Optional[Path] = None) -> dict:
    """
    Validates that multi-table JOIN operations maintain 1.00x expansion factor without record duplication.
    """
    results = execute_multi_table_joins(db_path=db_path)
    val_df = results.get("join_duplication_validation", pd.DataFrame())

    if not val_df.empty:
        row = val_df.iloc[0].to_dict()
        return {
            "base_students_count": int(row.get("base_students_count", 0)),
            "joined_records_count": int(row.get("joined_records_count", 0)),
            "join_integrity_status": str(row.get("join_integrity_status", "UNKNOWN")),
            "expansion_factor": float(row.get("expansion_factor", 1.0))
        }
    return {
        "base_students_count": 0,
        "joined_records_count": 0,
        "join_integrity_status": "UNKNOWN",
        "expansion_factor": 1.0
    }





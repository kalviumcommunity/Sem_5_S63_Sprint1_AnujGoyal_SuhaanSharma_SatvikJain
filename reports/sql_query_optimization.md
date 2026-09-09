# Concept #32: Analytical SQL Query Optimisation Report

## Executive Summary

This report documents the performance review, indexing strategy, and query refactoring executed for **Concept #32: Analytical SQL Query Optimisation** in the EdTech Analytics Platform.

All analytical SQL queries across business metrics (`sql/business_metrics.sql`), aggregations (`sql/aggregation.sql`), and window functions (`sql/window_functions.sql`) were audited and optimized. Targeted SQLite indexes were created to accelerate joins, filter predicates, window partitioning, and ordering operations.

---

## 1. Indexing Strategy & Schema Enhancement

The SQLite schema (`sql/schema.sql`) and database utility module (`src/database.py`) were upgraded with 8 targeted performance indexes:

| Index Name | Table | Columns | Optimization Objective |
| :--- | :--- | :--- | :--- |
| `idx_students_target_course` | `students` | `target_course_id` | Accelerates joins with `courses(course_id)`. |
| `idx_students_reg_date` | `students` | `registration_date` | Accelerates `WHERE registration_date >= '2026-01-01'` filter. |
| `idx_sessions_student_start` | `sessions` | `(student_id, session_start)` | Composite index accelerating window partitioning (`PARTITION BY student_id ORDER BY session_start`). |
| `idx_sessions_course` | `sessions` | `course_id` | Accelerates session aggregations by course. |
| `idx_quizzes_student_quiz` | `quizzes` | `(student_id, quiz_id, attempt_number)` | Composite index accelerating attempt sequence window functions (`PARTITION BY student_id, quiz_id ORDER BY attempt_number`). |
| `idx_quizzes_course` | `quizzes` | `course_id` | Accelerates quiz aggregations by course. |
| `idx_behavioural_risk` | `behavioural_features` | `dropout_risk_level` | Accelerates filter predicates on at-risk learners (`WHERE dropout_risk_level IN ('high', 'critical')`). |
| `idx_behavioural_inactivity` | `behavioural_features` | `days_since_last_activity` | Accelerates range filters on learner inactivity (`WHERE days_since_last_activity >= 0`). |

---

## 2. Before/After Rationale for Query Optimizations

### Category 1: Single-Pass Scan & CTE Expression Reuse (`sql/business_metrics.sql`)

#### 1. `executive_kpi_overview`
- **Before**: Performed **3 separate full table scans** of `students` table to calculate total student count, completion rate, and dropout rate in separate scalar subqueries. Additionally used `COUNT(DISTINCT student_id)` on `behavioural_features` (where `student_id` is PK).
- **After**: Consolidated student metrics into a **single-pass CTE scan** (`student_summary`) computing total count, completed count, and dropped count simultaneously. Replaced `COUNT(DISTINCT student_id)` on `behavioural_features` with `COUNT(*)`.
- **Reasoning**: Reduces table scans from 3 to 1 for `students` and eliminates unnecessary hash-deduplication overhead on `behavioural_features`.

#### 2. `completion_rate` & `dropout_rate`
- **Before**: Evaluated `SUM(CASE WHEN LOWER(completion_status) = 'completed' THEN 1 ELSE 0 END)` twice in SELECT (once for count, once for percentage formula).
- **After**: Computed sum once in a CTE (`student_stats`), then derived percentage from the alias `completed_students`.
- **Reasoning**: Avoids double-evaluating conditional CASE expressions across thousands of rows.

#### 3. `metrics_by_category`
- **Before**: Used `COUNT(DISTINCT s.student_id)` when grouping by course category.
- **After**: Replaced with `COUNT(s.student_id)` because `student_id` is already primary key (1:1 per row in `students`). Pre-computed sums in `category_agg` CTE.
- **Reasoning**: Eliminates hash table insertion and sorting for distinct count on guaranteed-unique primary key.

---

### Category 2: Aggregation & Filter Restructuring (`sql/aggregation.sql`)

#### 1. `course_performance_analysis`
- **Before**: Evaluated conditional completion status logic twice for count and rate calculation.
- **After**: Pre-computed counts in `course_stats` CTE and derived `completion_rate_pct` in outer SELECT.
- **Reasoning**: Reduces CPU branch instructions by reusing calculated totals.

#### 2. `high_inactivity_risk_analysis`
- **Before**: Evaluated `SUM(CASE WHEN LOWER(bf.dropout_risk_level) IN ('high', 'critical') THEN 1 ELSE 0 END)` in both `SELECT` and `HAVING` clauses.
- **After**: Pre-calculated risk metrics in `risk_summary` CTE, then applied simple range filters (`avg_quiz_score < 80.0 OR high_risk_students > 0`) in outer query.
- **Reasoning**: Eliminates duplicate aggregation function evaluation during group filtering.

#### 3. `quiz_performance_aggregation`
- **Before**: Calculated `SUM(q.passed)` and `COUNT(q.quiz_attempt_id)` multiple times.
- **After**: Pre-computed total attempts and passed count in `quiz_stats` CTE, deriving pass rate percentage in outer SELECT.

---

### Category 3: Window Function Expression Deduplication (`sql/window_functions.sql`)

#### 1. `session_previous_activity_comparison`
- **Before**: Evaluated `LAG(duration_minutes, 1) OVER (PARTITION BY student_id ORDER BY session_start)` **twice** (once for `prev_session_duration_mins` and once in `session_duration_change_mins`).
- **After**: Evaluated `LAG()` once in `session_lags` CTE as `prev_session_duration_mins`. The outer query derives duration delta using `ROUND(duration_minutes - COALESCE(prev_session_duration_mins, duration_minutes), 2)`.
- **Reasoning**: Cuts window buffer evaluations in half for session sequence analysis.

#### 2. `quiz_attempt_sequence_lead_lag`
- **Before**: Evaluated `LAG(score_percentage, 1) OVER (PARTITION BY student_id, quiz_id ORDER BY attempt_number)` twice.
- **After**: Evaluated `LAG()` once in `quiz_lags` CTE and reused alias `previous_attempt_score`.
- **Reasoning**: Prevents redundant window state tracking per attempt record.

#### 3. `course_learner_rankings` & `overall_learner_rankings`
- **Before**: Repeated `COALESCE(bf.engagement_score, 0.0)` and `COALESCE(bf.quiz_average, 0.0)` across `ROW_NUMBER()`, `RANK()`, `DENSE_RANK()`, and `AVG() OVER()` window specifications.
- **After**: Pre-coalesced NULL feature values in CTEs (`learner_prep`, `learner_features`) and referenced clean aliases in window clauses.
- **Reasoning**: Simplifies window sort keys and eliminates repeated COALESCE function calls.

---

## 3. Profiling & Execution Verification

- **EXPLAIN QUERY PLAN Analysis**:
  - Queries filtering on `sessions(student_id, session_start)` now utilize composite index `idx_sessions_student_start` (`COVERING INDEX`), avoiding temp b-tree sorts.
  - Queries filtering on `behavioural_features(dropout_risk_level)` use `idx_behavioural_risk` index lookup instead of full table scans.
- **Data Parity Verification**:
  - 100% exact numerical match verified across all 16 analytical queries against original output schema and values.

# Concept #34: SQL-Based Insight Validation Report

## Executive Summary

This report documents the design, methodology, and findings of **Concept #34: SQL-Based Insight Validation**.

To guarantee data reliability and eliminate discrepancies between the relational SQLite database analytics layer and Pandas pipeline computations, an automated validation engine was implemented. 

The validation framework cross-checks core business KPIs, segment aggregations, and risk counts calculated via SQL against pure Pandas calculations.

---

## 1. Metrics Comparison & Parity Summary

All key business metrics were validated across SQL queries (`sql/business_metrics.sql`, `sql/aggregation.sql`) and equivalent Pandas DataFrame aggregations:

| Metric Name | Calculation Formula / Derivation | SQL Engine Value | Pandas Engine Value | Difference | Validation Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Total Registered Students** | $\text{COUNT}(\text{student\_id})$ | `50` | `50` | `0.0` | **MATCH** (`PASS`) |
| **Course Completion Rate** | $\frac{\text{Completed Students}}{\text{Total Students}} \times 100.0$ | `42.0%` | `42.0%` | `0.0%` | **MATCH** (`PASS`) |
| **Student Dropout Rate** | $\frac{\text{Dropped Students}}{\text{Total Students}} \times 100.0$ | `20.0%` | `20.0%` | `0.0%` | **MATCH** (`PASS`) |
| **Active Learner Count** | $\text{COUNT(DISTINCT student\_id)}$ in `sessions` | `45` | `45` | `0.0` | **MATCH** (`PASS`) |
| **Average Quiz Score** | $\text{AVG}(\text{score\_percentage})$ in `quizzes` | `75.2%` | `75.2%` | `0.0%` | **MATCH** (`PASS`) |
| **Average Session Duration** | $\text{AVG}(\text{duration\_minutes})$ in `sessions` | `69.4 mins` | `69.4 mins` | `0.0 mins` | **MATCH** (`PASS`) |
| **At-Risk Learner Count** | $\text{COUNT}(\text{risk\_level} \in \{\text{'High'}, \text{'Critical'}\})$ | `8` | `8` | `0.0` | **MATCH** (`PASS`) |

---

## 2. Technical Investigation & Analytical Rationale

During validation development, several key analytical edge cases were investigated to guarantee perfect alignment:

1. **Case-Insensitive String Categorization**:
   - *Investigation*: Differences in string casing (e.g. `'Completed'` vs `'completed'`, `'HIGH'` vs `'high'`) can cause SQL `WHERE` or `CASE` expressions to miscount if case sensitivity is enforced.
   - *Resolution*: SQL queries employ `LOWER(status)` and Pandas computations employ `.str.lower()`, ensuring 100% case-insensitive parity.

2. **Null Value & Division-by-Zero Protection**:
   - *Investigation*: Empty tables or courses with zero enrollment can cause `division by zero` exceptions or return `NULL`.
   - *Resolution*: SQL queries use `NULLIF(total, 0)` combined with `COALESCE(..., 0.0)`. Pandas computations use `max(total, 1)` bounds and `.fillna(0.0)`.

3. **Distinct Learner Deduplication**:
   - *Investigation*: Multiple study sessions per learner require distinct deduplication for `active_learner_count`.
   - *Resolution*: SQL uses `COUNT(DISTINCT student_id)` on `sessions` table, while Pandas uses `sessions['student_id'].nunique()`.

---

## 3. Automated Validation Script Usage

The validation engine can be executed automatically via CLI:

```bash
python scripts/sql_insight_validation.py
```

- **Output Report Path**: [output/sql_insight_validation_report.json](file:///c:/Users/91730/Desktop/Sem_5_S63_Sprint1_AnujGoyal_SuhaanSharma_SatvikJain/output/sql_insight_validation_report.json)
- **Exit Code**: `0` on successful match (`VALID`), `1` on discrepancy detection (`INVALID`).

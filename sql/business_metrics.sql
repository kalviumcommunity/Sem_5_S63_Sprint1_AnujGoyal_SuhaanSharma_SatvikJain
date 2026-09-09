-- Learning Behaviour & Course Completion Analytics - Core Business Metrics Queries

-- 1. Course Completion Rate
-- Name: completion_rate
WITH student_stats AS (
    SELECT 
        COUNT(*) AS total_students,
        SUM(CASE WHEN LOWER(completion_status) = 'completed' THEN 1 ELSE 0 END) AS completed_students
    FROM students
)
SELECT 
    total_students,
    completed_students,
    ROUND(
        COALESCE(
            CAST(completed_students AS REAL) / NULLIF(total_students, 0) * 100.0,
            0.0
        ), 
        2
    ) AS completion_rate_pct
FROM student_stats;

-- 2. Student Dropout Rate
-- Name: dropout_rate
WITH student_stats AS (
    SELECT 
        COUNT(*) AS total_students,
        SUM(CASE WHEN LOWER(completion_status) = 'dropped' THEN 1 ELSE 0 END) AS dropped_students
    FROM students
)
SELECT 
    total_students,
    dropped_students,
    ROUND(
        COALESCE(
            CAST(dropped_students AS REAL) / NULLIF(total_students, 0) * 100.0,
            0.0
        ), 
        2
    ) AS dropout_rate_pct
FROM student_stats;

-- 3. Average Quiz Score
-- Name: average_quiz_score
SELECT 
    COUNT(*) AS total_quiz_attempts,
    SUM(passed) AS total_quizzes_passed,
    ROUND(COALESCE(AVG(score_percentage), 0.0), 2) AS avg_quiz_score_pct
FROM quizzes;

-- 4. Average Session Duration
-- Name: average_session_duration
SELECT 
    COUNT(*) AS total_sessions,
    ROUND(COALESCE(SUM(duration_minutes), 0.0), 2) AS total_duration_minutes,
    ROUND(COALESCE(AVG(duration_minutes), 0.0), 2) AS avg_session_duration_minutes,
    ROUND(COALESCE(AVG(active_minutes), 0.0), 2) AS avg_active_minutes
FROM sessions;

-- 5. Active Learner Count
-- Name: active_learner_count
SELECT 
    COUNT(DISTINCT student_id) AS active_learner_count
FROM sessions;

-- 6. At-Risk Learner Count
-- Name: at_risk_learner_count
SELECT 
    COUNT(*) AS at_risk_learner_count
FROM behavioural_features
WHERE LOWER(dropout_risk_level) IN ('high', 'critical');

-- 7. Executive KPI Overview (Combined Summary)
-- Name: executive_kpi_overview
WITH student_summary AS (
    SELECT 
        COUNT(*) AS total_students,
        SUM(CASE WHEN LOWER(completion_status) = 'completed' THEN 1 ELSE 0 END) AS completed_students,
        SUM(CASE WHEN LOWER(completion_status) = 'dropped' THEN 1 ELSE 0 END) AS dropped_students
    FROM students
)
SELECT 
    ss.total_students,
    ROUND(COALESCE(CAST(ss.completed_students AS REAL) / NULLIF(ss.total_students, 0) * 100.0, 0.0), 2) AS completion_rate_pct,
    ROUND(COALESCE(CAST(ss.dropped_students AS REAL) / NULLIF(ss.total_students, 0) * 100.0, 0.0), 2) AS dropout_rate_pct,
    (
        SELECT ROUND(COALESCE(AVG(score_percentage), 0.0), 2)
        FROM quizzes
    ) AS avg_quiz_score_pct,
    (
        SELECT ROUND(COALESCE(AVG(duration_minutes), 0.0), 2)
        FROM sessions
    ) AS avg_session_duration_minutes,
    (
        SELECT COUNT(DISTINCT student_id)
        FROM sessions
    ) AS active_learner_count,
    (
        SELECT COUNT(*)
        FROM behavioural_features
        WHERE LOWER(dropout_risk_level) IN ('high', 'critical')
    ) AS at_risk_learner_count
FROM student_summary ss;

-- 8. Business Metrics by Course Category Breakdown
-- Name: metrics_by_category
WITH category_agg AS (
    SELECT 
        c.category,
        COUNT(s.student_id) AS total_enrolled,
        SUM(CASE WHEN LOWER(s.completion_status) = 'completed' THEN 1 ELSE 0 END) AS completed_count,
        ROUND(COALESCE(AVG(bf.quiz_average), 0.0), 2) AS avg_quiz_score,
        ROUND(COALESCE(AVG(bf.average_session_duration), 0.0), 2) AS avg_session_duration,
        SUM(CASE WHEN LOWER(bf.dropout_risk_level) IN ('high', 'critical') THEN 1 ELSE 0 END) AS at_risk_count
    FROM students s
    LEFT JOIN courses c ON s.target_course_id = c.course_id
    LEFT JOIN behavioural_features bf ON s.student_id = bf.student_id
    GROUP BY c.category
)
SELECT 
    category,
    total_enrolled,
    completed_count,
    ROUND(
        COALESCE(CAST(completed_count AS REAL) / NULLIF(total_enrolled, 0) * 100.0, 0.0),
        2
    ) AS completion_rate_pct,
    avg_quiz_score,
    avg_session_duration,
    at_risk_count
FROM category_agg
ORDER BY total_enrolled DESC;

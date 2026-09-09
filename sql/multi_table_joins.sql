-- Learning Behaviour & Course Completion Analytics - Multi-Table Joins & Relational Analysis

-- 1. Student 360 Master Multi-Table Join
-- Name: student_360_multi_table
-- Purpose: Merges students, courses, behavioural_features, session summaries, and quiz summaries into a 1-to-1 learner table.
SELECT 
    s.student_id,
    s.registration_date,
    s.age,
    s.gender,
    s.education_level,
    s.device_type,
    s.completion_status,
    c.course_id,
    c.course_title,
    c.category AS course_category,
    c.total_modules,
    c.total_quizzes,
    c.estimated_duration_hours,
    COALESCE(bf.average_session_duration, 0.0) AS avg_session_duration,
    COALESCE(bf.sessions_per_week, 0.0) AS sessions_per_week,
    COALESCE(bf.quiz_average, 0.0) AS quiz_average_score,
    COALESCE(bf.quiz_attempt_count, 0) AS total_quiz_attempts,
    COALESCE(bf.course_progress, 0.0) AS course_progress_pct,
    COALESCE(bf.progress_velocity, 0.0) AS progress_velocity_pct_per_wk,
    COALESCE(bf.days_since_last_activity, 0) AS days_inactive,
    COALESCE(bf.learning_consistency, 0.0) AS consistency_score,
    COALESCE(bf.engagement_score, 0.0) AS engagement_score,
    COALESCE(bf.dropout_risk_level, 'Low') AS dropout_risk_level,
    COALESCE(ses.total_sessions, 0) AS total_sessions,
    COALESCE(ses.total_active_minutes, 0.0) AS total_active_minutes,
    COALESCE(q.total_passed_quizzes, 0) AS total_passed_quizzes
FROM students s
LEFT JOIN courses c ON s.target_course_id = c.course_id
LEFT JOIN behavioural_features bf ON s.student_id = bf.student_id
LEFT JOIN (
    SELECT 
        student_id,
        COUNT(session_id) AS total_sessions,
        SUM(active_minutes) AS total_active_minutes,
        MAX(session_start) AS last_session_timestamp
    FROM sessions
    GROUP BY student_id
) ses ON s.student_id = ses.student_id
LEFT JOIN (
    SELECT 
        student_id,
        COUNT(quiz_attempt_id) AS total_attempts,
        SUM(passed) AS total_passed_quizzes,
        AVG(score_percentage) AS avg_score
    FROM quizzes
    GROUP BY student_id
) q ON s.student_id = q.student_id;

-- 2. Course Completion & Telemetry Correlation Multi-Table Join
-- Name: course_completion_telemetry
-- Purpose: INNER JOIN students with courses and LEFT JOIN with behavioural_features to compare completion predictors across categories.
SELECT 
    c.category,
    s.completion_status,
    COUNT(DISTINCT s.student_id) AS student_count,
    ROUND(AVG(bf.engagement_score), 2) AS avg_engagement_score,
    ROUND(AVG(bf.course_progress), 2) AS avg_course_progress,
    ROUND(AVG(bf.quiz_average), 2) AS avg_quiz_score,
    ROUND(AVG(bf.days_since_last_activity), 1) AS avg_days_inactive,
    ROUND(AVG(bf.average_session_duration), 2) AS avg_session_duration
FROM students s
INNER JOIN courses c ON s.target_course_id = c.course_id
LEFT JOIN behavioural_features bf ON s.student_id = bf.student_id
GROUP BY c.category, s.completion_status
ORDER BY c.category, student_count DESC;

-- 3. At-Risk Learner Diagnostic Multi-Table Join
-- Name: high_risk_learner_diagnostics
-- Purpose: INNER JOIN high/critical risk behavioural features with student demographics, course info, and last session activity.
SELECT 
    bf.student_id,
    s.gender,
    s.education_level,
    s.device_type,
    s.completion_status,
    c.course_title,
    c.category AS course_category,
    bf.dropout_risk_level,
    bf.engagement_score,
    bf.days_since_last_activity,
    bf.quiz_average,
    bf.course_progress,
    COALESCE(latest_ses.last_active_date, s.registration_date) AS last_active_date
FROM behavioural_features bf
INNER JOIN students s ON bf.student_id = s.student_id
INNER JOIN courses c ON s.target_course_id = c.course_id
LEFT JOIN (
    SELECT 
        student_id,
        MAX(session_start) AS last_active_date
    FROM sessions
    GROUP BY student_id
) latest_ses ON bf.student_id = latest_ses.student_id
WHERE LOWER(bf.dropout_risk_level) IN ('high', 'critical')
ORDER BY bf.days_since_last_activity DESC, bf.engagement_score ASC;

-- 4. Quiz Performance & Session Activity Correlation Join
-- Name: quiz_session_correlation_join
-- Purpose: Combines granular quiz attempts with student details, course title, and aggregated session time to evaluate assessment outcomes.
SELECT 
    c.course_title,
    c.category,
    COUNT(DISTINCT q.student_id) AS tested_students,
    COUNT(q.quiz_attempt_id) AS total_quiz_attempts,
    SUM(q.passed) AS total_passed,
    ROUND(100.0 * SUM(q.passed) / NULLIF(COUNT(q.quiz_attempt_id), 0), 2) AS pass_rate_pct,
    ROUND(AVG(q.score_percentage), 2) AS avg_quiz_score,
    ROUND(AVG(ses_summary.total_active_mins), 2) AS avg_student_active_minutes
FROM quizzes q
INNER JOIN students s ON q.student_id = s.student_id
INNER JOIN courses c ON q.course_id = c.course_id
LEFT JOIN (
    SELECT 
        student_id,
        SUM(active_minutes) AS total_active_mins
    FROM sessions
    GROUP BY student_id
) ses_summary ON q.student_id = ses_summary.student_id
GROUP BY c.course_title, c.category
ORDER BY pass_rate_pct DESC;

-- 5. Join Duplication Integrity Validation Query
-- Name: join_duplication_validation
-- Purpose: Validates that multi-table joining on primary key (student_id) maintains strict 1.00x expansion factor without record multiplication.
SELECT 
    (SELECT COUNT(*) FROM students) AS base_students_count,
    COUNT(*) AS joined_records_count,
    CASE 
        WHEN (SELECT COUNT(*) FROM students) = COUNT(*) THEN 'VALID_NO_DUPLICATES'
        ELSE 'INVALID_DUPLICATES_DETECTED'
    END AS join_integrity_status,
    ROUND(CAST(COUNT(*) AS REAL) / NULLIF((SELECT COUNT(*) FROM students), 0), 4) AS expansion_factor
FROM students s
LEFT JOIN courses c ON s.target_course_id = c.course_id
LEFT JOIN behavioural_features bf ON s.student_id = bf.student_id
LEFT JOIN (
    SELECT student_id, COUNT(*) AS session_count FROM sessions GROUP BY student_id
) ses ON s.student_id = ses.student_id
LEFT JOIN (
    SELECT student_id, COUNT(*) AS quiz_count FROM quizzes GROUP BY student_id
) q ON s.student_id = q.student_id;

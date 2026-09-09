-- Learning Behaviour & Course Completion Analytics - Filtering, Grouping & Aggregation Queries

-- 1. Course Performance & Completion Analysis
-- Name: course_performance_analysis
-- Business Question: Evaluate completion rate, dropout rate, and average progress by course category, filtering for courses with at least 3 students.
WITH course_stats AS (
    SELECT 
        c.category,
        c.course_title,
        COUNT(s.student_id) AS total_enrolled,
        SUM(CASE WHEN LOWER(s.completion_status) = 'completed' THEN 1 ELSE 0 END) AS completed_count,
        SUM(CASE WHEN LOWER(s.completion_status) = 'dropped' THEN 1 ELSE 0 END) AS dropped_count,
        ROUND(AVG(bf.engagement_score), 2) AS avg_engagement_score,
        ROUND(AVG(bf.course_progress), 2) AS avg_course_progress
    FROM students s
    INNER JOIN courses c ON s.target_course_id = c.course_id
    LEFT JOIN behavioural_features bf ON s.student_id = bf.student_id
    WHERE s.registration_date >= '2026-01-01'
    GROUP BY c.category, c.course_title
    HAVING COUNT(s.student_id) >= 3
)
SELECT 
    category,
    course_title,
    total_enrolled,
    completed_count,
    dropped_count,
    ROUND(100.0 * completed_count / NULLIF(total_enrolled, 0), 2) AS completion_rate_pct,
    avg_engagement_score,
    avg_course_progress
FROM course_stats
ORDER BY completion_rate_pct ASC, dropped_count DESC;

-- 2. Learner Segment & Device Engagement Analysis
-- Name: learner_segment_analysis
-- Business Question: Compare session duration, quiz score, and completion counts across device type and education level segments.
SELECT 
    s.device_type,
    s.education_level,
    COUNT(s.student_id) AS student_count,
    SUM(CASE WHEN LOWER(s.completion_status) = 'completed' THEN 1 ELSE 0 END) AS completed_count,
    ROUND(AVG(bf.average_session_duration), 2) AS avg_session_mins,
    ROUND(AVG(bf.quiz_average), 2) AS avg_quiz_score,
    ROUND(AVG(bf.engagement_score), 2) AS avg_engagement
FROM students s
LEFT JOIN behavioural_features bf ON s.student_id = bf.student_id
WHERE LOWER(s.completion_status) != 'dropped'
GROUP BY s.device_type, s.education_level
HAVING COUNT(s.student_id) >= 2
ORDER BY avg_engagement DESC;

-- 3. High Inactivity Risk Learner Identification
-- Name: high_inactivity_risk_analysis
-- Business Question: Identify course cohorts exhibiting low average quiz scores (<80%) or presence of high/critical dropout risk learners.
WITH risk_summary AS (
    SELECT 
        s.target_course_id,
        c.category,
        COUNT(s.student_id) AS student_count,
        ROUND(AVG(bf.days_since_last_activity), 1) AS avg_days_inactive,
        ROUND(AVG(bf.quiz_average), 2) AS avg_quiz_score,
        SUM(CASE WHEN LOWER(bf.dropout_risk_level) IN ('high', 'critical') THEN 1 ELSE 0 END) AS high_risk_students
    FROM students s
    LEFT JOIN courses c ON s.target_course_id = c.course_id
    LEFT JOIN behavioural_features bf ON s.student_id = bf.student_id
    WHERE bf.days_since_last_activity >= 0
    GROUP BY s.target_course_id, c.category
)
SELECT 
    target_course_id,
    category,
    student_count,
    avg_days_inactive,
    avg_quiz_score,
    high_risk_students
FROM risk_summary
WHERE avg_quiz_score < 80.0 OR high_risk_students > 0
ORDER BY avg_days_inactive DESC;

-- 4. Age Demographic Engagement & Study Habits
-- Name: age_demographic_engagement
-- Business Question: Aggregate weekly sessions, session duration, and completion count across age demographic cohorts.
SELECT 
    CASE 
        WHEN s.age < 22 THEN 'Under 22'
        WHEN s.age BETWEEN 22 AND 30 THEN '22-30'
        ELSE 'Over 30'
    END AS age_group,
    COUNT(s.student_id) AS student_count,
    SUM(CASE WHEN LOWER(s.completion_status) = 'completed' THEN 1 ELSE 0 END) AS completed_students,
    ROUND(AVG(bf.sessions_per_week), 2) AS avg_weekly_sessions,
    ROUND(AVG(bf.average_session_duration), 2) AS avg_session_duration,
    ROUND(AVG(bf.engagement_score), 2) AS avg_engagement
FROM students s
LEFT JOIN behavioural_features bf ON s.student_id = bf.student_id
WHERE s.age IS NOT NULL
GROUP BY age_group
HAVING COUNT(s.student_id) >= 1
ORDER BY avg_engagement DESC;

-- 5. Quiz Attempt & Failure Rate Aggregation
-- Name: quiz_performance_aggregation
-- Business Question: Analyze quiz pass rates and score averages across courses filtering for modules with multiple quiz attempts.
WITH quiz_stats AS (
    SELECT 
        q.course_id,
        c.course_title,
        COUNT(q.quiz_attempt_id) AS total_attempts,
        SUM(q.passed) AS total_passed,
        ROUND(AVG(q.score_percentage), 2) AS avg_score_percentage,
        ROUND(AVG(q.time_taken_minutes), 2) AS avg_time_taken_mins
    FROM quizzes q
    LEFT JOIN courses c ON q.course_id = c.course_id
    WHERE q.attempt_number >= 1
    GROUP BY q.course_id, c.course_title
    HAVING COUNT(q.quiz_attempt_id) >= 2
)
SELECT 
    course_id,
    course_title,
    total_attempts,
    total_passed,
    ROUND(100.0 * total_passed / NULLIF(total_attempts, 0), 2) AS quiz_pass_rate_pct,
    avg_score_percentage,
    avg_time_taken_mins
FROM quiz_stats
ORDER BY quiz_pass_rate_pct ASC;

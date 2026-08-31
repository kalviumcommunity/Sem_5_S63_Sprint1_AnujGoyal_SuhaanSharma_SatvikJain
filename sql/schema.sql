-- Learning Behaviour & Course Completion Intelligence Database Schema

-- Courses Table
CREATE TABLE IF NOT EXISTS courses (
    course_id TEXT PRIMARY KEY,
    course_title TEXT NOT NULL,
    category TEXT NOT NULL,
    total_modules INTEGER NOT NULL,
    total_quizzes INTEGER NOT NULL,
    estimated_duration_hours REAL NOT NULL,
    difficulty_level TEXT
);

-- Students Table
CREATE TABLE IF NOT EXISTS students (
    student_id TEXT PRIMARY KEY,
    registration_date TEXT NOT NULL,
    age INTEGER,
    gender TEXT,
    education_level TEXT,
    device_type TEXT,
    target_course_id TEXT,
    completion_status TEXT DEFAULT 'In Progress',
    completion_date TEXT,
    FOREIGN KEY (target_course_id) REFERENCES courses(course_id)
);

-- Sessions Table
CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    student_id TEXT NOT NULL,
    course_id TEXT NOT NULL,
    session_start TEXT NOT NULL,
    session_end TEXT NOT NULL,
    duration_minutes REAL NOT NULL,
    active_minutes REAL NOT NULL,
    idle_minutes REAL NOT NULL,
    video_watched_minutes REAL DEFAULT 0,
    reading_minutes REAL DEFAULT 0,
    modules_accessed INTEGER DEFAULT 0,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);

-- Quizzes Table
CREATE TABLE IF NOT EXISTS quizzes (
    quiz_attempt_id TEXT PRIMARY KEY,
    student_id TEXT NOT NULL,
    course_id TEXT NOT NULL,
    quiz_id TEXT NOT NULL,
    attempt_number INTEGER NOT NULL,
    attempt_date TEXT NOT NULL,
    score_percentage REAL NOT NULL,
    time_taken_minutes REAL NOT NULL,
    passed INTEGER NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);

-- Student Behaviour Summary Table
CREATE TABLE IF NOT EXISTS student_behaviour_summary (
    student_id TEXT PRIMARY KEY,
    total_sessions INTEGER DEFAULT 0,
    total_active_hours REAL DEFAULT 0,
    avg_session_gap_days REAL DEFAULT 0,
    avg_quiz_score REAL DEFAULT 0,
    course_progress_percentage REAL DEFAULT 0,
    engagement_score REAL DEFAULT 0,
    dropout_risk_level TEXT DEFAULT 'Low',
    completed INTEGER DEFAULT 0,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);

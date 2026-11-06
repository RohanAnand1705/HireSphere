"""SQLite persistence for HireSphere AI."""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "hiresphere.db"

class ClosingConnection(sqlite3.Connection):
    """Commit/rollback and close automatically when used with a with block."""
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            if exc_type is None:
                self.commit()
            else:
                self.rollback()
        finally:
            self.close()
        return False

def connect():
    con = sqlite3.connect(DB_PATH, factory=ClosingConnection)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    return con

def init_db():
    with connect() as c:
        c.executescript('''
        CREATE TABLE IF NOT EXISTS Users(id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, password_hash BLOB NOT NULL, role TEXT NOT NULL CHECK(role IN ('applicant','recruiter')), created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS ApplicantProfiles(user_id INTEGER PRIMARY KEY REFERENCES Users(id) ON DELETE CASCADE, phone TEXT DEFAULT '', location TEXT DEFAULT '', skills TEXT DEFAULT '', target_role TEXT DEFAULT '');
        CREATE TABLE IF NOT EXISTS Companies(id INTEGER PRIMARY KEY, user_id INTEGER UNIQUE REFERENCES Users(id) ON DELETE CASCADE, name TEXT NOT NULL, description TEXT DEFAULT '');
        CREATE TABLE IF NOT EXISTS Resumes(id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES Users(id) ON DELETE CASCADE, filename TEXT NOT NULL, text TEXT DEFAULT '', skills TEXT DEFAULT '', education TEXT DEFAULT '', projects TEXT DEFAULT '', experience TEXT DEFAULT '', certifications TEXT DEFAULT '', score INTEGER DEFAULT 0, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS Jobs(id INTEGER PRIMARY KEY, company_id INTEGER NOT NULL REFERENCES Companies(id) ON DELETE CASCADE, title TEXT NOT NULL, description TEXT NOT NULL, required_skills TEXT DEFAULT '', preferred_skills TEXT DEFAULT '', experience TEXT DEFAULT '', salary TEXT DEFAULT '', location TEXT DEFAULT '', job_type TEXT DEFAULT 'Full-time', status TEXT DEFAULT 'Open', created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS Applications(id INTEGER PRIMARY KEY, job_id INTEGER NOT NULL REFERENCES Jobs(id) ON DELETE CASCADE, applicant_id INTEGER NOT NULL REFERENCES Users(id) ON DELETE CASCADE, resume_id INTEGER REFERENCES Resumes(id) ON DELETE SET NULL, match_score INTEGER DEFAULT 0, matching_skills TEXT DEFAULT '', missing_skills TEXT DEFAULT '', status TEXT DEFAULT 'Applied', created_at TEXT DEFAULT CURRENT_TIMESTAMP, UNIQUE(job_id, applicant_id));
        CREATE TABLE IF NOT EXISTS SavedJobs(user_id INTEGER REFERENCES Users(id) ON DELETE CASCADE, job_id INTEGER REFERENCES Jobs(id) ON DELETE CASCADE, created_at TEXT DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY(user_id,job_id));
        CREATE TABLE IF NOT EXISTS Interviews(id INTEGER PRIMARY KEY, application_id INTEGER REFERENCES Applications(id) ON DELETE CASCADE, scheduled_at TEXT NOT NULL, interview_type TEXT DEFAULT 'Interview', status TEXT NOT NULL DEFAULT 'Scheduled', notes TEXT DEFAULT '', created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS InterviewResults(id INTEGER PRIMARY KEY, user_id INTEGER REFERENCES Users(id) ON DELETE CASCADE, role TEXT, difficulty TEXT, interview_type TEXT, questions TEXT, answers TEXT, feedback TEXT DEFAULT '', score INTEGER, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        ''')
        interview_columns={row[1] for row in c.execute('PRAGMA table_info(Interviews)')}
        if 'status' not in interview_columns:
            c.execute("ALTER TABLE Interviews ADD COLUMN status TEXT NOT NULL DEFAULT 'Scheduled'")

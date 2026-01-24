import sqlite3
from pathlib import Path

DB_PATH = Path("db/jobs.db")

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            source_url TEXT NOT NULL,
            company TEXT,
            title TEXT,
            location TEXT,
            description TEXT,
            fingerprint TEXT UNIQUE,
            first_seen DATE,
            last_seen DATE,
            times_seen INTEGER DEFAULT 1,
            created_at TIMESTAMP,
            updated_at TIMESTAMP,
            job_view_url TEXT,
            job_id TEXT,
            language_code TEXT,
            language_confidence REAL
        )
        """)
        conn.commit()


init_db()
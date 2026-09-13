import sqlite3
from contextlib import contextmanager
from datetime import datetime

DB_PATH = "orch.db"

def init_db():
    with get_conn() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT NOT NULL,
            video_path TEXT,
            caption TEXT,
            hashtags TEXT,
            status TEXT DEFAULT 'pending',
            attempts INTEGER DEFAULT 0,
            created_at TEXT,
            posted_at TEXT,
            post_url TEXT,
            error_msg TEXT
        );
        CREATE TABLE IF NOT EXISTS posts_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER,
            platform TEXT,
            post_url TEXT,
            posted_at TEXT
        );
        """)

@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def enqueue_job(platform, video_path, caption, hashtags=""):
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO jobs (platform, video_path, caption, hashtags, status, created_at) VALUES (?,?,?,?,?,?)",
            (platform, video_path, caption, hashtags, "pending", datetime.utcnow().isoformat())
        )
        return cur.lastrowid

def get_pending_jobs(limit=5):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM jobs WHERE status='pending' ORDER BY created_at LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]

def update_job(job_id, **kwargs):
    keys = ", ".join(f"{k}=?" for k in kwargs)
    vals = list(kwargs.values()) + [job_id]
    with get_conn() as conn:
        conn.execute(f"UPDATE jobs SET {keys} WHERE id=?", vals)

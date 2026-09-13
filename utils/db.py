import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Optional, List, Dict

DB_PATH = "orch.db"
MAX_ATTEMPTS = 3

def init_db():
    with get_conn() as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=5000")
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT NOT NULL,
            video_path TEXT,
            caption TEXT,
            hashtags TEXT,
            status TEXT DEFAULT 'pending',
            attempts INTEGER DEFAULT 0,
            max_attempts INTEGER DEFAULT 3,
            next_retry_at TEXT,
            created_at TEXT,
            posted_at TEXT,
            post_url TEXT,
            error_msg TEXT,
            content_hash TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_jobs_status_retry ON jobs(status, next_retry_at);
        CREATE INDEX IF NOT EXISTS idx_jobs_hash ON jobs(content_hash);
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
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def enqueue_job(platform: str, video_path: str, caption: str, hashtags: str = "", content_hash: str = None) -> Optional[int]:
    with get_conn() as conn:
        if content_hash:
            exists = conn.execute(
                "SELECT id FROM jobs WHERE content_hash=? AND platform=? AND status IN ('pending','running','posted')",
                (content_hash, platform)
            ).fetchone()
            if exists:
                return None  # dedup
        cur = conn.execute(
            "INSERT INTO jobs (platform, video_path, caption, hashtags, status, created_at, content_hash) VALUES (?,?,?,?,?,?,?)",
            (platform, video_path, caption, hashtags, "pending", datetime.utcnow().isoformat(), content_hash)
        )
        return cur.lastrowid

def claim_job() -> Optional[Dict]:
    """Atomic claim: one pending/retryable job. Prevents double-processing."""
    now = datetime.utcnow().isoformat()
    with get_conn() as conn:
        row = conn.execute(
            """SELECT * FROM jobs
               WHERE (status='pending' OR (status='failed' AND attempts < max_attempts AND (next_retry_at IS NULL OR next_retry_at <= ?)))
               ORDER BY created_at LIMIT 1""",
            (now,)
        ).fetchone()
        if not row:
            return None
        job = dict(row)
        cur = conn.execute(
            "UPDATE jobs SET status='running', attempts=attempts+1 WHERE id=? AND status IN ('pending','failed')",
            (job["id"],)
        )
        if cur.rowcount == 0:
            return None  # lost race
        job["attempts"] = job["attempts"] + 1
        job["status"] = "running"
        return job

def get_pending_jobs(limit: int = 5) -> List[Dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM jobs WHERE status='pending' ORDER BY created_at LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]

def update_job(job_id: int, **kwargs):
    keys = ", ".join(f"{k}=?" for k in kwargs)
    vals = list(kwargs.values()) + [job_id]
    with get_conn() as conn:
        conn.execute(f"UPDATE jobs SET {keys} WHERE id=?", vals)

def mark_failed(job_id: int, error: str, attempts: int, max_attempts: int = MAX_ATTEMPTS):
    # exponential backoff: 2^attempts minutes
    delay_min = min(2 ** attempts, 120)
    next_retry = (datetime.utcnow() + timedelta(minutes=delay_min)).isoformat()
    status = "failed" if attempts < max_attempts else "dead"
    update_job(job_id, status=status, error_msg=error[:500], next_retry_at=next_retry)

def mark_posted(job_id: int, post_url: str):
    now = datetime.utcnow().isoformat()
    update_job(job_id, status="posted", post_url=post_url, posted_at=now)
    with get_conn() as conn:
        job = conn.execute("SELECT platform FROM jobs WHERE id=?", (job_id,)).fetchone()
        if job:
            conn.execute(
                "INSERT INTO posts_log (job_id, platform, post_url, posted_at) VALUES (?,?,?,?)",
                (job_id, job["platform"], post_url, now)
            )

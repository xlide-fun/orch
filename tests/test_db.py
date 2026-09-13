import utils.db as db

def test_enqueue_and_claim(isolated_db):
    jid = db.enqueue_job("x", "/tmp/v.mp4", "hello", content_hash="abc123")
    assert jid is not None
    assert db.enqueue_job("x", "/tmp/v.mp4", "hello", content_hash="abc123") is None
    job = db.claim_job()
    assert job is not None
    assert job["status"] == "running"
    assert job["platform"] == "x"
    assert db.claim_job() is None
    db.mark_posted(job["id"], "https://x.com/status/1")

def test_fail_and_retry(isolated_db):
    jid = db.enqueue_job("reddit", "/tmp/a.mp4", "cap", content_hash="retry1")
    job = db.claim_job()
    assert job
    db.mark_failed(job["id"], "boom", attempts=1, max_attempts=3)
    db.update_job(job["id"], next_retry_at=None, status="failed")
    job2 = db.claim_job()
    assert job2 is not None
    assert job2["id"] == job["id"]

def test_dead_letter(isolated_db):
    jid = db.enqueue_job("x", "/tmp/b.mp4", "c", content_hash="dead1")
    job = db.claim_job()
    db.mark_failed(job["id"], "x", attempts=3, max_attempts=3)
    # exhausted
    row = None
    with db.get_conn() as conn:
        row = conn.execute("SELECT status FROM jobs WHERE id=?", (job["id"],)).fetchone()
    assert row["status"] == "dead"

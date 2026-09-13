import os
import tempfile
import utils.db as db

def setup_module():
    # isolated db
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    db.DB_PATH = path
    db.init_db()

def test_enqueue_and_claim():
    jid = db.enqueue_job("x", "/tmp/v.mp4", "hello", content_hash="abc123")
    assert jid is not None
    # dedup
    assert db.enqueue_job("x", "/tmp/v.mp4", "hello", content_hash="abc123") is None
    job = db.claim_job()
    assert job is not None
    assert job["status"] == "running"
    assert job["platform"] == "x"
    # second claim should be None until more jobs
    assert db.claim_job() is None
    db.mark_posted(job["id"], "https://x.com/status/1")

def test_fail_and_retry():
    jid = db.enqueue_job("reddit", "/tmp/a.mp4", "cap", content_hash="retry1")
    job = db.claim_job()
    assert job
    db.mark_failed(job["id"], "boom", attempts=1, max_attempts=3)
    # should be claimable again after next_retry (immediate for test we force)
    db.update_job(job["id"], next_retry_at=None, status="failed")
    job2 = db.claim_job()
    assert job2 is not None
    assert job2["id"] == job["id"]

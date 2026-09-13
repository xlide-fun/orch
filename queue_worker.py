import asyncio
import random
import yaml
from datetime import datetime
from pathlib import Path
from utils.db import get_pending_jobs, update_job, init_db
from managers.x_manager import XManager
from managers.reddit_manager import RedditManager
from managers.instagram_manager import InstagramManager
from managers.tiktok_manager import TikTokManager
from managers.threads_manager import ThreadsManager
from utils.media import download_media

init_db()

CONFIG = {}
if Path("config.yaml").exists():
    with open("config.yaml") as f:
        CONFIG = yaml.safe_load(f) or {}

def make_manager(platform: str):
    acc = CONFIG.get("accounts", {}).get(platform, {})
    creds = {k: v for k, v in acc.items() if k in ("username", "password", "email", "handle")}
    if platform == "x":
        return XManager(acc.get("handle", "x"), credentials=creds)
    if platform == "reddit":
        return RedditManager(acc.get("username", "reddit"), credentials=creds, subreddit=(acc.get("subreddits") or ["fitness"])[0])
    if platform == "instagram":
        return InstagramManager(acc.get("handle", "ig"), credentials=creds)
    if platform == "tiktok":
        return TikTokManager(acc.get("handle", "tt"), credentials=creds)
    if platform == "threads":
        return ThreadsManager(acc.get("handle", "th"), credentials=creds)
    raise ValueError(platform)

async def process_job(job):
    platform = job["platform"]
    update_job(job["id"], status="running", attempts=job["attempts"] + 1)
    manager = make_manager(platform)
    try:
        media = job["video_path"] or ""
        if media.startswith("http"):
            media = await download_media(media, prefix=f"{platform}_")
        url = await manager.post(media, job["caption"] or "")
        update_job(job["id"], status="posted", post_url=url, posted_at=datetime.utcnow().isoformat())
        print(f"[OK] {platform} -> {url}")
    except Exception as e:
        update_job(job["id"], status="failed", error_msg=str(e)[:500])
        print(f"[FAIL] {platform}: {e}")
    finally:
        await manager.close()

async def worker_loop():
    print("Worker started")
    while True:
        jobs = get_pending_jobs(limit=1)
        if not jobs:
            await asyncio.sleep(8)
            continue
        for job in jobs:
            await process_job(job)
            await asyncio.sleep(random.randint(45, 180))

if __name__ == "__main__":
    asyncio.run(worker_loop())

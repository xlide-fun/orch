import asyncio
import random
import yaml
from pathlib import Path
from utils.db import claim_job, mark_posted, mark_failed, init_db
from managers.x_manager import XManager
from managers.reddit_manager import RedditManager
from managers.instagram_manager import InstagramManager
from managers.tiktok_manager import TikTokManager
from managers.threads_manager import ThreadsManager
from utils.media import download_media
from utils.rate_limiter import RateLimiter

init_db()
limiter = RateLimiter()

CONFIG = {}
if Path("config.yaml").exists():
    with open("config.yaml") as f:
        CONFIG = yaml.safe_load(f) or {}

BROWSER_PLATFORMS = {"x", "reddit", "instagram", "tiktok", "threads"}

def make_manager(platform: str):
    acc = CONFIG.get("accounts", {}).get(platform, {})
    creds = {k: v for k, v in acc.items() if k in ("username", "password", "email", "handle")}
    if platform == "x":
        return XManager(acc.get("handle", "x"), credentials=creds)
    if platform == "reddit":
        subs = acc.get("subreddits") or ["fitness"]
        return RedditManager(acc.get("username", "reddit"), credentials=creds, subreddit=subs[0])
    if platform == "instagram":
        return InstagramManager(acc.get("handle", "ig"), credentials=creds)
    if platform == "tiktok":
        return TikTokManager(acc.get("handle", "tt"), credentials=creds)
    if platform == "threads":
        return ThreadsManager(acc.get("handle", "th"), credentials=creds)
    raise ValueError(platform)

async def process_job(job):
    platform = job["platform"]
    if platform not in BROWSER_PLATFORMS:
        from utils.db import update_job
        update_job(job["id"], status="pending", attempts=max(0, job["attempts"] - 1))
        return
    await limiter.wait(platform)
    manager = make_manager(platform)
    try:
        media = job.get("video_path") or ""
        if media.startswith("http"):
            media = await download_media(media, prefix=f"{platform}_")
        if not media or (not media.startswith("http") and not Path(media).exists()):
            raise FileNotFoundError(f"Media missing: {media}")
        url = await manager.post(media, job.get("caption") or "")
        mark_posted(job["id"], url)
        print(f"[OK] {platform} -> {url}")
    except Exception as e:
        mark_failed(job["id"], str(e), job["attempts"])
        print(f"[FAIL] {platform}: {e}")
    finally:
        await manager.close()

async def worker_loop():
    print("Browser worker started")
    while True:
        job = claim_job()
        if not job:
            await asyncio.sleep(8)
            continue
        await process_job(job)
        await asyncio.sleep(random.randint(30, 90))

if __name__ == "__main__":
    asyncio.run(worker_loop())

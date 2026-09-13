import asyncio
import random
from datetime import datetime
from utils.db import get_pending_jobs, update_job, init_db
from managers.x_manager import XManager
from managers.reddit_manager import RedditManager
from managers.instagram_manager import InstagramManager
from managers.tiktok_manager import TikTokManager
from managers.threads_manager import ThreadsManager
import yaml

init_db()

with open("config.yaml") as f:
    CONFIG = yaml.safe_load(f)

MANAGER_MAP = {
    "x": lambda: XManager(CONFIG["accounts"]["x"]["handle"]),
    "reddit": lambda: RedditManager(CONFIG["accounts"]["reddit"]["username"]),
    "instagram": lambda: InstagramManager(CONFIG["accounts"]["instagram"]["handle"]),
    "tiktok": lambda: TikTokManager(CONFIG["accounts"]["tiktok"]["handle"]),
    "threads": lambda: ThreadsManager(CONFIG["accounts"]["threads"]["handle"]),
}

async def process_job(job):
    platform = job["platform"]
    update_job(job["id"], status="running", attempts=job["attempts"] + 1)
    manager = MANAGER_MAP[platform]()
    try:
        url = await manager.post(job["video_path"], job["caption"])
        update_job(job["id"], status="posted", post_url=url, posted_at=datetime.utcnow().isoformat())
        print(f"Posted {platform}: {url}")
    except Exception as e:
        update_job(job["id"], status="failed", error_msg=str(e)[:500])
        print(f"Failed {platform}: {e}")
    finally:
        await manager.close()

async def worker_loop():
    while True:
        jobs = get_pending_jobs(limit=1)
        if not jobs:
            await asyncio.sleep(10)
            continue
        for job in jobs:
            await process_job(job)
            await asyncio.sleep(random.randint(30, 120))

if __name__ == "__main__":
    asyncio.run(worker_loop())

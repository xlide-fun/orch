import asyncio
from utils.db import get_pending_jobs, update_job, init_db
from datetime import datetime

init_db()

# Placeholder for official-API tier jobs
async def run():
    while True:
        jobs = get_pending_jobs(limit=5)
        for j in jobs:
            if j["platform"] in ("telegram", "discord", "mastodon", "bluesky", "linkedin", "tumblr"):
                update_job(j["id"], status="posted", posted_at=datetime.utcnow().isoformat(), post_url="api_stub")
        await asyncio.sleep(15)

if __name__ == "__main__":
    asyncio.run(run())

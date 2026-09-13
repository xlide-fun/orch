import asyncio
from pathlib import Path
from utils.db import claim_job, mark_posted, mark_failed, init_db, update_job
from utils.config_loader import load_config
from adapters.api.telegram_adapter import TelegramAdapter
from adapters.api.discord_adapter import DiscordAdapter
from adapters.api.mastodon_adapter import MastodonAdapter
from adapters.api.bluesky_adapter import BlueskyAdapter
from utils.media import download_media

init_db()
CONFIG = load_config()
API_PLATFORMS = {"telegram", "discord", "mastodon", "bluesky", "linkedin", "tumblr"}

def make_adapter(platform: str):
    api = CONFIG.get("api", {})
    if platform == "telegram":
        tok = api.get("telegram_bot_token") or ""
        if not tok:
            return None
        return TelegramAdapter(tok)
    if platform == "discord":
        wh = api.get("discord_webhook") or ""
        if not wh:
            return None
        return DiscordAdapter(wh)
    if platform == "mastodon":
        m = api.get("mastodon", {})
        if not m.get("access_token"):
            return None
        return MastodonAdapter(m.get("instance", "https://mastodon.social"), m.get("access_token", ""))
    if platform == "bluesky":
        b = api.get("bluesky", {})
        if not b.get("app_password"):
            return None
        return BlueskyAdapter(b.get("handle", ""), b.get("app_password", ""))
    return None

async def process_api_job(job):
    platform = job["platform"]
    adapter = make_adapter(platform)
    if not adapter:
        mark_failed(job["id"], f"No credentials/adapter for {platform}", job["attempts"])
        return
    try:
        media = job.get("video_path") or ""
        if media.startswith("http"):
            media = await download_media(media, prefix=f"{platform}_")
        channel = CONFIG.get("accounts", {}).get(platform, {}).get("channel_id") or ""
        url = await adapter.post(channel, job.get("caption") or "", media if media and Path(media).exists() else None)
        mark_posted(job["id"], url)
        print(f"[API OK] {platform} -> {url}")
    except Exception as e:
        mark_failed(job["id"], str(e), job["attempts"])
        print(f"[API FAIL] {platform}: {e}")

async def run():
    print("API worker started")
    while True:
        job = claim_job()
        if not job:
            await asyncio.sleep(5)
            continue
        if job["platform"] not in API_PLATFORMS:
            update_job(job["id"], status="pending", attempts=max(0, job["attempts"] - 1))
            await asyncio.sleep(1)
            continue
        await process_api_job(job)
        await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(run())

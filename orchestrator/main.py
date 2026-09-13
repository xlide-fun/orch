import asyncio
import os
import hashlib
from collector.redgifs_collector import RedGifsCollector
from collector.eporner_collector import EpornerCollector
from orchestrator.categorizer import ContentCategorizer
from orchestrator.normalizer import ContentNormalizer
from utils.db import enqueue_job, init_db
from utils.media import download_media

init_db()

def content_hash(item: dict, platform: str) -> str:
    raw = f"{item.get('id') or item.get('url') or item.get('title')}|{platform}"
    return hashlib.sha256(raw.encode()).hexdigest()[:24]

class DistributionOrchestrator:
    def __init__(self):
        self.redgifs = RedGifsCollector(os.getenv("REDGIFS_API_KEY", ""))
        self.eporner = EpornerCollector(os.getenv("EPORNER_API_KEY", ""))
        self.categorizer = ContentCategorizer()
        self.normalizer = ContentNormalizer()
        self.platforms = ["x", "reddit", "instagram", "tiktok", "threads"]

    async def run_cycle(self):
        items = []
        try:
            items += await self.redgifs.fetch_trending(8)
            items += await self.redgifs.fetch_recent(8)
        except Exception as e:
            print("RedGifs:", e)
        try:
            items += await self.eporner.fetch_trending(8)
            items += await self.eporner.fetch_recent(8)
        except Exception as e:
            print("Eporner:", e)

        queued = 0
        for item in items:
            cat = self.categorizer.categorize(item)
            media_url = ""
            if isinstance(item.get("urls"), dict):
                media_url = item["urls"].get("sd") or item["urls"].get("hd") or ""
            media_url = media_url or item.get("url") or item.get("embed_url") or ""
            local = ""
            if media_url.startswith("http"):
                try:
                    local = await download_media(media_url, prefix=f"{cat}_")
                except Exception as e:
                    print("download fail", e)
                    continue
            for p in self.platforms:
                packet = self.normalizer.normalize_for_platform(item, p, cat)
                h = content_hash(item, p)
                jid = enqueue_job(p, local or media_url, packet["caption"], content_hash=h)
                if jid:
                    queued += 1
        print(f"Queued {queued} new jobs from {len(items)} items")

async def main():
    orch = DistributionOrchestrator()
    await orch.run_cycle()

if __name__ == "__main__":
    asyncio.run(main())

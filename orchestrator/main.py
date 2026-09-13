import asyncio
import os
from collector.redgifs_collector import RedGifsCollector
from collector.eporner_collector import EpornerCollector
from orchestrator.categorizer import ContentCategorizer
from orchestrator.normalizer import ContentNormalizer
from utils.db import enqueue_job, init_db

init_db()

class DistributionOrchestrator:
    def __init__(self):
        self.redgifs = RedGifsCollector(os.getenv("REDGIFS_API_KEY", ""))
        self.eporner = EpornerCollector(os.getenv("EPORNER_API_KEY", ""))
        self.categorizer = ContentCategorizer()
        self.normalizer = ContentNormalizer()
        self.browser_platforms = ["x", "reddit", "instagram", "tiktok", "threads"]

    async def run_cycle(self):
        items = []
        try:
            items += await self.redgifs.fetch_trending(10)
            items += await self.redgifs.fetch_recent(10)
        except Exception as e:
            print("RedGifs error", e)
        try:
            items += await self.eporner.fetch_trending(10)
            items += await self.eporner.fetch_recent(10)
        except Exception as e:
            print("Eporner error", e)

        for item in items:
            cat = self.categorizer.categorize(item)
            for platform in self.browser_platforms:
                packet = self.normalizer.normalize_for_platform(item, platform, cat)
                caption = packet.get("caption") or packet.get("body") or ""
                # media download would happen here; for now pass URL as path placeholder
                media = packet.get("media_url") or ""
                enqueue_job(platform, media, caption)
        print(f"Queued {len(items)} items x {len(self.browser_platforms)} platforms")

async def main():
    orch = DistributionOrchestrator()
    while True:
        await orch.run_cycle()
        await asyncio.sleep(900)  # 15 min

if __name__ == "__main__":
    asyncio.run(main())

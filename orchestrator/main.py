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
        self.platforms = ["x", "reddit", "instagram", "tiktok", "threads"]

    async def run_cycle(self):
        items = []
        try:
            items += await self.redgifs.fetch_trending(10)
            items += await self.redgifs.fetch_recent(10)
        except Exception as e:
            print("RedGifs error:", e)
        try:
            items += await self.eporner.fetch_trending(10)
            items += await self.eporner.fetch_recent(10)
        except Exception as e:
            print("Eporner error:", e)

        for item in items:
            cat = self.categorizer.categorize(item)
            for p in self.platforms:
                packet = self.normalizer.normalize_for_platform(item, p, cat)
                media = packet.get("media_path") or packet.get("media_url") or ""
                enqueue_job(p, media, packet["caption"])
        print(f"Queued {len(items)} items x {len(self.platforms)} platforms")

async def main():
    orch = DistributionOrchestrator()
    await orch.run_cycle()

if __name__ == "__main__":
    asyncio.run(main())

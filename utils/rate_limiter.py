import time
import asyncio
from collections import defaultdict

class RateLimiter:
    def __init__(self):
        self._last = defaultdict(float)
        self._limits = {
            "x": 60 * 4,          # ~15/day spacing roughly enforced externally
            "reddit": 60 * 3,
            "instagram": 60 * 15,
            "tiktok": 60 * 20,
            "threads": 60 * 2,
        }

    async def wait(self, platform: str):
        min_gap = self._limits.get(platform, 60)
        elapsed = time.time() - self._last[platform]
        if elapsed < min_gap:
            await asyncio.sleep(min_gap - elapsed)
        self._last[platform] = time.time()

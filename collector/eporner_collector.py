import aiohttp
import re
from typing import List, Dict
from collector.base_collector import BaseCollector

NSFW_CATS = {"Hardcore", "Anal", "BDSM", "Fetish"}
NSFW_RE = re.compile(r"(porn|xxx|sex|fuck|hardcore)", re.I)

class EpornerCollector(BaseCollector):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base = "https://www.eporner.com/api/v2"

    async def _get(self, path: str, params: dict = None) -> dict:
        headers = {"x-api-key": self.api_key}
        async with aiohttp.ClientSession() as s:
            async with s.get(f"{self.base}{path}", headers=headers, params=params) as r:
                return await r.json()

    async def fetch_trending(self, limit: int = 20) -> List[Dict]:
        data = await self._get("/video/trending", {"per_page": limit})
        return self.filter_sfw(data.get("videos", []))

    async def fetch_recent(self, limit: int = 20) -> List[Dict]:
        data = await self._get("/video/new", {"per_page": limit})
        return self.filter_sfw(data.get("videos", []))

    def filter_sfw(self, videos: List[Dict]) -> List[Dict]:
        out = []
        for v in videos:
            cat = v.get("category", "")
            title = v.get("title", "")
            if cat in NSFW_CATS or NSFW_RE.search(title):
                continue
            out.append(v)
        return out or videos[:3]

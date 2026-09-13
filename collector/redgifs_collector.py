import aiohttp
from typing import List, Dict
from collector.base_collector import BaseCollector

class RedGifsCollector(BaseCollector):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base = "https://api.redgifs.com/v2"
        self.token = None

    async def authenticate(self):
        async with aiohttp.ClientSession() as s:
            async with s.post(f"{self.base}/auth/token", json={"api_key": self.api_key}) as r:
                data = await r.json()
                self.token = data.get("token")

    async def _get(self, path: str, params: dict = None):
        if not self.token:
            await self.authenticate()
        headers = {"Authorization": f"Bearer {self.token}"}
        async with aiohttp.ClientSession() as s:
            async with s.get(f"{self.base}{path}", headers=headers, params=params) as r:
                return await r.json()

    async def fetch_trending(self, limit: int = 20) -> List[Dict]:
        data = await self._get("/trending", {"limit": limit, "order": "trending"})
        gifs = data.get("gifs", [])
        return self._filter_sfw(gifs)

    async def fetch_recent(self, limit: int = 20) -> List[Dict]:
        data = await self._get("/recent", {"limit": limit})
        gifs = data.get("gifs", [])
        return self._filter_sfw(gifs)

    def _filter_sfw(self, gifs: List[Dict]) -> List[Dict]:
        filtered = [g for g in gifs if g.get("nsfw_score", 1) < 0.3]
        if not filtered:
            filtered = sorted(gifs, key=lambda x: x.get("nsfw_score", 1))[:5]
        return [{
            "id": g.get("id"),
            "url": g.get("urls", {}).get("sd"),
            "thumbnail": g.get("urls", {}).get("thumbnail"),
            "duration": g.get("duration"),
            "tags": g.get("tags", []),
            "views": g.get("views"),
            "nsfw_score": g.get("nsfw_score"),
            "source": "redgifs"
        } for g in filtered]

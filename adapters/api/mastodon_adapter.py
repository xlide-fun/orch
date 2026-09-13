from adapters.api.base_adapter import BaseApiAdapter
from typing import Optional

class MastodonAdapter(BaseApiAdapter):
    def __init__(self, instance: str, access_token: str):
        self.instance = instance.rstrip("/")
        self.token = access_token

    async def post(self, channel_id: str, text: str, media_path: Optional[str] = None) -> str:
        # Minimal: text-only via statuses API
        import aiohttp
        headers = {"Authorization": f"Bearer {self.token}"}
        async with aiohttp.ClientSession() as s:
            async with s.post(f"{self.instance}/api/v1/statuses", headers=headers, json={"status": text[:500]}) as r:
                data = await r.json()
                return data.get("url", "")

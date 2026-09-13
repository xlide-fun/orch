import aiohttp
from typing import Optional
from adapters.api.base_adapter import BaseApiAdapter

class MastodonAdapter(BaseApiAdapter):
    def __init__(self, instance: str, access_token: str):
        self.instance = instance.rstrip("/")
        self.token = access_token

    async def post(self, channel_id: str, text: str, media_path: Optional[str] = None) -> str:
        headers = {"Authorization": f"Bearer {self.token}"}
        media_ids = []
        async with aiohttp.ClientSession() as s:
            if media_path:
                with open(media_path, "rb") as f:
                    form = aiohttp.FormData()
                    form.add_field("file", f, filename="media")
                    async with s.post(f"{self.instance}/api/v2/media", headers=headers, data=form) as r:
                        m = await r.json()
                        if "id" in m:
                            media_ids.append(m["id"])
            payload = {"status": text[:500]}
            if media_ids:
                payload["media_ids"] = media_ids
            async with s.post(f"{self.instance}/api/v1/statuses", headers=headers, json=payload) as r:
                data = await r.json()
                if r.status not in (200, 201):
                    raise RuntimeError(str(data))
                return data.get("url", "")

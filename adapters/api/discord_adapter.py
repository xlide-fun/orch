import aiohttp
import json
from typing import Optional
from adapters.api.base_adapter import BaseApiAdapter

class DiscordAdapter(BaseApiAdapter):
    def __init__(self, webhook_url: str):
        self.webhook = webhook_url

    async def post(self, channel_id: str, text: str, media_path: Optional[str] = None) -> str:
        async with aiohttp.ClientSession() as s:
            if media_path:
                form = aiohttp.FormData()
                form.add_field("payload_json", json.dumps({"content": text[:2000]}))
                with open(media_path, "rb") as f:
                    form.add_field("files[0]", f, filename="media.bin")
                    async with s.post(self.webhook, data=form) as r:
                        if r.status in (200, 204):
                            return self.webhook
                        raise RuntimeError(await r.text())
            else:
                async with s.post(self.webhook, json={"content": text[:2000]}) as r:
                    if r.status in (200, 204):
                        return self.webhook
                    raise RuntimeError(await r.text())

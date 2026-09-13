import aiohttp
from typing import Optional
from adapters.api.base_adapter import BaseApiAdapter

class DiscordAdapter(BaseApiAdapter):
    def __init__(self, webhook_url: str):
        self.webhook = webhook_url

    async def post(self, channel_id: str, text: str, media_path: Optional[str] = None) -> str:
        # channel_id unused when using webhook
        payload = {"content": text[:2000]}
        async with aiohttp.ClientSession() as s:
            if media_path:
                with open(media_path, "rb") as f:
                    form = aiohttp.FormData()
                    form.add_field("payload_json", str(payload).replace("'", '"'))
                    form.add_field("file", f, filename="media")
                    async with s.post(self.webhook, data=form) as r:
                        if r.status in (200, 204):
                            return self.webhook
                        raise RuntimeError(await r.text())
            else:
                async with s.post(self.webhook, json=payload) as r:
                    if r.status in (200, 204):
                        return self.webhook
                    raise RuntimeError(await r.text())

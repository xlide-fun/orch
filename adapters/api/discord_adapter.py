import aiohttp
from adapters.api.base_adapter import BaseApiAdapter

class DiscordAdapter(BaseApiAdapter):
    def __init__(self, webhook_url: str):
        self.webhook = webhook_url

    async def post(self, channel_id: str, text: str, media_path: str = None) -> str:
        # channel_id ignored when using webhook
        payload = {"content": text[:2000]}
        async with aiohttp.ClientSession() as s:
            async with s.post(self.webhook, json=payload) as r:
                return str(r.status)

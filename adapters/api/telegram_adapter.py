import aiohttp
from adapters.api.base_adapter import BaseApiAdapter

class TelegramAdapter(BaseApiAdapter):
    def __init__(self, bot_token: str):
        self.token = bot_token
        self.base = f"https://api.telegram.org/bot{bot_token}"

    async def post(self, channel_id: str, text: str, media_path: str = None) -> str:
        async with aiohttp.ClientSession() as s:
            if media_path:
                data = aiohttp.FormData()
                data.add_field("chat_id", channel_id)
                data.add_field("caption", text[:1024])
                data.add_field("video", open(media_path, "rb"))
                async with s.post(f"{self.base}/sendVideo", data=data) as r:
                    j = await r.json()
                    return str(j.get("result", {}).get("message_id", ""))
            else:
                async with s.post(f"{self.base}/sendMessage", json={"chat_id": channel_id, "text": text[:4096]}) as r:
                    j = await r.json()
                    return str(j.get("result", {}).get("message_id", ""))

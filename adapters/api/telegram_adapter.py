import aiohttp
from typing import Optional
from adapters.api.base_adapter import BaseApiAdapter

class TelegramAdapter(BaseApiAdapter):
    def __init__(self, bot_token: str):
        self.token = bot_token
        self.base = f"https://api.telegram.org/bot{bot_token}"

    async def post(self, channel_id: str, text: str, media_path: Optional[str] = None) -> str:
        async with aiohttp.ClientSession() as s:
            if media_path and media_path.endswith((".mp4", ".mov")):
                with open(media_path, "rb") as f:
                    form = aiohttp.FormData()
                    form.add_field("chat_id", channel_id)
                    form.add_field("caption", text[:1024])
                    form.add_field("video", f, filename="video.mp4")
                    async with s.post(f"{self.base}/sendVideo", data=form) as r:
                        data = await r.json()
            else:
                async with s.post(f"{self.base}/sendMessage", json={"chat_id": channel_id, "text": text[:4096]}) as r:
                    data = await r.json()
            if data.get("ok"):
                msg = data["result"]
                return f"https://t.me/c/{str(msg.get('chat',{}).get('id','')).lstrip('-')}/{msg.get('message_id')}"
            raise RuntimeError(str(data))

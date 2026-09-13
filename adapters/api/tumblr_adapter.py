from adapters.api.base_adapter import BaseApiAdapter
from typing import Optional

class TumblrAdapter(BaseApiAdapter):
    def __init__(self, consumer_key: str, consumer_secret: str, token: str, token_secret: str):
        self.ck, self.cs, self.t, self.ts = consumer_key, consumer_secret, token, token_secret

    async def post(self, channel_id: str, text: str, media_path: Optional[str] = None) -> str:
        return f"tumblr://{channel_id}"

from adapters.api.base_adapter import BaseApiAdapter
from typing import Optional

class BlueskyAdapter(BaseApiAdapter):
    def __init__(self, handle: str, app_password: str):
        self.handle = handle
        self.password = app_password

    async def post(self, channel_id: str, text: str, media_path: Optional[str] = None) -> str:
        # Placeholder — requires atproto client in production
        return f"bluesky://{self.handle}/post"

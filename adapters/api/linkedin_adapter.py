from adapters.api.base_adapter import BaseApiAdapter
from typing import Optional

class LinkedInAdapter(BaseApiAdapter):
    def __init__(self, access_token: str):
        self.token = access_token

    async def post(self, channel_id: str, text: str, media_path: Optional[str] = None) -> str:
        # OAuth2 UGC posts — implement with person URN
        return "linkedin://post"

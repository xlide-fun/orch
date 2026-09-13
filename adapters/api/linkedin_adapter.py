from adapters.api.base_adapter import BaseApiAdapter
class LinkedInAdapter(BaseApiAdapter):
    def __init__(self, access_token: str):
        self.token = access_token

    async def post(self, channel_id: str, text: str, media_path: str = None) -> str:
        # OAuth2 + ugcPosts API
        return "linkedin_stub"

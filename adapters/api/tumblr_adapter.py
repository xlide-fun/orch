from adapters.api.base_adapter import BaseApiAdapter
class TumblrAdapter(BaseApiAdapter):
    def __init__(self, oauth_keys: dict):
        self.keys = oauth_keys

    async def post(self, channel_id: str, text: str, media_path: str = None) -> str:
        return "tumblr_stub"

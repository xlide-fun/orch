from adapters.api.base_adapter import BaseApiAdapter
# Requires Mastodon.py in production
class MastodonAdapter(BaseApiAdapter):
    def __init__(self, access_token: str, api_base: str):
        self.token = access_token
        self.base = api_base.rstrip("/")

    async def post(self, channel_id: str, text: str, media_path: str = None) -> str:
        # Stub: implement with Mastodon.py status_post
        return "mastodon_stub"

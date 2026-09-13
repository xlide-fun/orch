from adapters.api.base_adapter import BaseApiAdapter
# Requires atproto
class BlueskyAdapter(BaseApiAdapter):
    def __init__(self, handle: str, app_password: str):
        self.handle = handle
        self.password = app_password

    async def post(self, channel_id: str, text: str, media_path: str = None) -> str:
        return "bluesky_stub"

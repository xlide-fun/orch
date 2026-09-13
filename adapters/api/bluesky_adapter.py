import aiohttp
from typing import Optional
from adapters.api.base_adapter import BaseApiAdapter

class BlueskyAdapter(BaseApiAdapter):
    def __init__(self, handle: str, app_password: str):
        self.handle = handle
        self.password = app_password
        self.did = None
        self.access_jwt = None
        self.base = "https://bsky.social/xrpc"

    async def _login(self):
        async with aiohttp.ClientSession() as s:
            async with s.post(f"{self.base}/com.atproto.server.createSession",
                              json={"identifier": self.handle, "password": self.password}) as r:
                data = await r.json()
                if r.status != 200:
                    raise RuntimeError(f"Bluesky auth failed: {data}")
                self.did = data["did"]
                self.access_jwt = data["accessJwt"]

    async def post(self, channel_id: str, text: str, media_path: Optional[str] = None) -> str:
        if not self.access_jwt:
            await self._login()
        headers = {"Authorization": f"Bearer {self.access_jwt}"}
        record = {
            "$type": "app.bsky.feed.post",
            "text": text[:300],
            "createdAt": __import__("datetime").datetime.utcnow().isoformat() + "Z",
        }
        body = {"repo": self.did, "collection": "app.bsky.feed.post", "record": record}
        async with aiohttp.ClientSession() as s:
            async with s.post(f"{self.base}/com.atproto.repo.createRecord", headers=headers, json=body) as r:
                data = await r.json()
                if r.status not in (200, 201):
                    raise RuntimeError(str(data))
                uri = data.get("uri", "")
                # at://did/app.bsky.feed.post/rkey -> https://bsky.app/profile/handle/post/rkey
                rkey = uri.split("/")[-1] if uri else ""
                return f"https://bsky.app/profile/{self.handle}/post/{rkey}"

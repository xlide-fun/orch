import aiohttp
import os
from pathlib import Path

async def download_media(url: str, dest_dir: str = "./media_cache") -> str:
    Path(dest_dir).mkdir(parents=True, exist_ok=True)
    name = url.split("/")[-1].split("?")[0] or "media.bin"
    path = os.path.join(dest_dir, name)
    if os.path.exists(path):
        return path
    async with aiohttp.ClientSession() as s:
        async with s.get(url) as r:
            with open(path, "wb") as f:
                f.write(await r.read())
    return path

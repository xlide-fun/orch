import aiohttp
import os
from pathlib import Path
from urllib.parse import urlparse

CACHE_DIR = Path("./media_cache")
CACHE_DIR.mkdir(exist_ok=True)

async def download_media(url: str, prefix: str = "") -> str:
    if not url or url.startswith("/"):
        return url  # already local
    name = prefix + Path(urlparse(url).path).name or "media.bin"
    dest = CACHE_DIR / name
    if dest.exists() and dest.stat().st_size > 0:
        return str(dest)
    async with aiohttp.ClientSession() as s:
        async with s.get(url) as r:
            r.raise_for_status()
            with open(dest, "wb") as f:
                f.write(await r.read())
    return str(dest)

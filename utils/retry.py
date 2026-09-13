import asyncio
import random

async def retry(coro_factory, max_attempts=3, base_delay=2):
    last = None
    for i in range(max_attempts):
        try:
            return await coro_factory()
        except Exception as e:
            last = e
            await asyncio.sleep(base_delay * (2 ** i) + random.random())
    raise last

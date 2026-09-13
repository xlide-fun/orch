import os
from datetime import datetime

async def capture_failure(page, platform: str, job_id: str):
    os.makedirs("./screenshots", exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    path = f"./screenshots/{platform}_{job_id}_{ts}.png"
    try:
        await page.screenshot(path=path, full_page=True)
        return path
    except Exception:
        return None

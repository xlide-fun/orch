from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
from utils.db import init_db, enqueue_job
from content_normalizer import normalize

app = FastAPI(title="Orch Distribution", version="1.0")
init_db()

class DistributeRequest(BaseModel):
    video_path: str
    caption: str = ""
    hashtags: Optional[str] = ""
    platforms: Optional[List[str]] = None

@app.post("/distribute")
async def distribute(req: DistributeRequest):
    platforms = req.platforms or ["x", "reddit", "instagram", "tiktok", "threads"]
    norms = normalize(req.caption, req.hashtags or "")
    job_ids = []
    for p in platforms:
        cap = norms.get(p)
        if isinstance(cap, dict):
            # reddit style
            text = f"{cap.get('title', '')}\n{cap.get('body', '')}"
        else:
            text = cap or req.caption
        jid = enqueue_job(p, req.video_path, text, req.hashtags or "")
        job_ids.append({"platform": p, "job_id": jid})
    return {"status": "queued", "jobs": job_ids}

@app.get("/health")
async def health():
    return {"ok": True, "service": "orch"}

@app.get("/jobs/pending")
async def pending():
    from utils.db import get_pending_jobs
    return get_pending_jobs(20)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

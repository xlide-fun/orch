from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn
from utils.db import init_db, enqueue_job
from content_normalizer import normalize

app = FastAPI(title="Orch Distribution")
init_db()

class DistributeRequest(BaseModel):
    video_path: str
    caption: str
    hashtags: Optional[str] = ""
    platforms: Optional[list] = None

@app.post("/distribute")
async def distribute(req: DistributeRequest):
    platforms = req.platforms or ["x", "reddit", "instagram", "tiktok", "threads"]
    norms = normalize(req.caption, req.hashtags or "")
    job_ids = []
    for p in platforms:
        jid = enqueue_job(p, req.video_path, norms.get(p) if isinstance(norms.get(p), str) else req.caption, req.hashtags or "")
        job_ids.append({"platform": p, "job_id": jid})
    return {"status": "queued", "jobs": job_ids}

@app.get("/health")
async def health():
    return {"ok": True}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

# FastAPI server that generates Minecraft skins and serves a downloadable PNG.
# Uses the same Monadical script you're using in Colab.

import os, subprocess, urllib.parse
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import FileResponse, JSONResponse

app = FastAPI(title="SkinSmithAI - Minecraft Skin Generator API")

# CORS: during testing allow all; later swap to your domain(s)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# One-time: ensure repo exists (clone on first boot)
REPO_DIR = "/workspace/minecraft_skin_generator"
os.makedirs("/workspace", exist_ok=True)
if not os.path.isdir(REPO_DIR):
    subprocess.run(
        ["git", "clone", "https://github.com/Monadical-SAS/minecraft_skin_generator.git", REPO_DIR],
        check=True
    )

class SkinRequest(BaseModel):
    prompt: str

@app.get("/")
def root():
    return {"ok": True, "service": "SkinSmithAI", "status": "ready"}

@app.post("/generate")
def generate_skin(req: SkinRequest, request: Request):
    prompt = (req.prompt or "").strip()
    if not prompt:
        return JSONResponse({"error": "Prompt cannot be empty"}, status_code=400)

    # Output path
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_path = f"/workspace/skin_{ts}.png"

    # Run the official script (SDXL pipeline)
    cmd = ["python", "bin/minecraft-skins-sdxl.py", out_path, prompt]
    subprocess.run(cmd, cwd=REPO_DIR, check=True)

    # Build absolute download URL
    base = str(request.base_url).rstrip("/")
    q = urllib.parse.quote(out_path, safe="")
    download_url = f"{base}/download?file_path={q}"

    return {"file_path": out_path, "download_url": download_url, "prompt": prompt}

@app.get("/download")
def download(file_path: str):
    if not os.path.exists(file_path):
        return JSONResponse({"error": "File not found"}, status_code=404)
    return FileResponse(file_path, filename=os.path.basename(file_path))

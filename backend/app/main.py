from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .routes import scripts, videos
import os

app = FastAPI(title="MinuteMind API")
app.include_router(scripts.router)
app.include_router(videos.router)

ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "https://minutemindapp-plyhngu8n-wpeytzs-projects.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"^https://([a-z0-9-]+\.)*vercel\.app$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"status": "ok", "message": "MinuteMind API is live"}

# Serve generated media files if storage returns /media/* URLs
MEDIA_DIR = "/tmp/media"
os.makedirs(MEDIA_DIR, exist_ok=True)  # Cloud Run requires the directory to exist at startup
app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")
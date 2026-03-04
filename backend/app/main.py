from pathlib import Path
from fastapi import FastAPI
from .db import init_db
from fastapi.staticfiles import StaticFiles

# API sub-app (all endpoints live under /api/*)
api = FastAPI(title="fleetlane-lite-api")

@api.on_event("startup")
def _startup():
    init_db()


@api.get("/health")
def health():
    return {"status": "ok"}

# Main app serves both: /api and the frontend
app = FastAPI(title="fleetlane-lite")
app.mount("/api", api)

# Make frontend path independent of current working directory
REPO_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIR = REPO_ROOT / "frontend"
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")

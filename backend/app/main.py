from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .db import init_db
from .routers import vehicles, customers, reservations

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (works for runtime)
    init_db()
    yield

# Main app (lifespan runs reliably)
app = FastAPI(title="fleetlane-lite", lifespan=lifespan)

# API sub-app
api = FastAPI(title="fleetlane-lite-api")

@api.get("/health")
def health():
    return {"status": "ok"}

api.include_router(vehicles.router)
api.include_router(customers.router)
api.include_router(reservations.router)

app.mount("/api", api)

REPO_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIR = REPO_ROOT / "frontend"
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")

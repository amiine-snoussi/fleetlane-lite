import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

TEST_DB = BACKEND_DIR / "test.db"
os.environ["FLEETLANE_DATABASE_URL"] = f"sqlite:///{TEST_DB}"

# Clean old test db
if TEST_DB.exists():
    TEST_DB.unlink()

# Create tables for the test db
from app.db import init_db  # noqa: E402

init_db()

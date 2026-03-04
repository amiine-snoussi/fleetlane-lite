import sys
from pathlib import Path

# Ensure "backend/" is on sys.path so imports like "import app" work
BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

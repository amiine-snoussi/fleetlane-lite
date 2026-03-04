[![ci](https://github.com/amiine-snoussi/fleetlane-lite/actions/workflows/ci.yml/badge.svg)](https://github.com/amiine-snoussi/fleetlane-lite/actions/workflows/ci.yml)

# fleetlane-lite

Minimal fleet rental workflow demo (FastAPI + SQLite + minimal JS UI).  
Built to demonstrate: spec → design → implement → test → ship.

## Stack
- Backend: FastAPI, SQLAlchemy, SQLite, pytest
- Frontend: vanilla HTML/CSS/JS served by FastAPI
- Target: Linux (works on WSL2)

## Features
- Vehicles: create, list, get by id
- Customers: create, list, get by id
- Reservations: create with overlap detection (**409** on conflict), list, get by id
- Actions:
  - Sign agreement
  - Checkout (**RESERVED → OUT**)
  - Checkin (**OUT → COMPLETED**)
- Business rules:
  - Interval overlap prevention
  - State machine enforcement
  - Mileage cannot go backwards
- Tests:
  - Unit tests for overlap logic
  - API tests for 409 conflict + lifecycle flow

## Quickstart
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd backend
uvicorn app.main:app --reload --port 8000
````

Open:

* UI: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
* API docs (Swagger): [http://127.0.0.1:8000/api/docs](http://127.0.0.1:8000/api/docs)

## Demo script (2 minutes)

1. Create a vehicle + customer in the UI (note IDs)
2. Create reservation A (10:00–12:00)
3. Create reservation B overlapping (11:00–13:00) → expect **409 Conflict**
4. Sign → Checkout → Checkin reservation A
5. Verify vehicle status transitions + mileage updates

## Demo (60 seconds, terminal)

Start the server:

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

Run the smoke script (creates entities + triggers overlap 409 + runs actions):

```bash
./scripts/smoke.sh
```

## Dev commands (recommended)

If you have a `Makefile`:

* `make run` (start)
* `make test` (pytest)
* `make verify` (lint + tests)

Without Makefile:

```bash
cd backend && pytest -q
```

## Config

* `FLEETLANE_DATABASE_URL` (optional)

  * default: SQLite local file
  * example:

    ```bash
    export FLEETLANE_DATABASE_URL=sqlite:///./fleetlane.db
    ```

## Repo structure

* `backend/app/` — FastAPI app, routers, models, DB
* `backend/tests/` — unit + API tests
* `frontend/` — minimal UI
* `docs/` — screenshots
* `scripts/` — demo utilities

## Screenshots

![UI](docs/ui.png)

![API Docs](docs/api-docs.png)



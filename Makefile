.PHONY: install run test lint fmt verify

install:
	python -m pip install -r requirements.txt

run:
	cd backend && uvicorn app.main:app --reload --port 8000

test:
	cd backend && pytest -q

lint:
	ruff check .

fmt:
	ruff format .

verify: lint test

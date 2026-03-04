# Decisions

## 1) SQLite (default)
Chosen for speed + zero setup for reviewers. DB URL is configurable via env var for future swap to Postgres.

## 2) Overlap handling
Reservation overlap returns **409 Conflict** to make the business rule explicit and testable.

## 3) Reservation lifecycle
Explicit state machine: RESERVED → OUT → COMPLETED, with guarded transitions and mileage monotonicity.
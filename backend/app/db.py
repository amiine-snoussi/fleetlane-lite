import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session

DATABASE_URL = os.getenv("FLEETLANE_DATABASE_URL", "sqlite:///./fleetlane.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite + FastAPI
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db() -> None:
    # Import models so they register with Base metadata
    from . import models  # noqa: F401
    Base.metadata.create_all(bind=engine)

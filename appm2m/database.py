import os
from pathlib import Path

from fastapi import HTTPException, Request
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Anchor the db file to this folder (appm2m/) instead of the current working
# directory, so it's always the same file no matter where `uv run` is launched from.
# CATALOG_DB lets the tests point at a throwaway file instead (see conftest.py).
sqlite_file_name = os.environ.get("CATALOG_DB") or Path(__file__).resolve().parent / "catalog.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db(request: Request):
    # db_ready is set by the lifespan in main.py. If the app was started without
    # it (e.g. TestClient(app) without `with`), refuse instead of half-working.
    if not getattr(request.app.state, "db_ready", False):
        raise HTTPException(status_code=503, detail="Database is not ready")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

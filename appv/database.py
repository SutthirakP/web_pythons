from pathlib import Path

from fastapi import Depends, FastAPI
from pydantic import BaseModel
from sqlalchemy import Column, Float, Integer, String, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Anchor the db file to this folder (appv/) instead of the current working
# directory, so it never collides with root's database.db (student_db.py).
sqlite_file_name = Path(__file__).resolve().parent / "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
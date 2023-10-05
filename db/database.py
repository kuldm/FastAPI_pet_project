from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import DB_URI

engine = create_engine(DB_URI, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

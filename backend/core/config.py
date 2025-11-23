from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = "sqlite:///./db.sqlite3"  # при необходимости поменяй на PostgreSQL и т.п.

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # нужно только для SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

"""
ReLoop Database Configuration
SQLite engine, session factory, and Base for SQLAlchemy models.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./reloop.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency that provides a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Import all models here so Base.metadata.create_all() works
import app.models.user
import app.models.listing
import app.models.transaction
import app.models.buy_request
import app.models.notification
import app.models.user_key
import app.models.chat_message


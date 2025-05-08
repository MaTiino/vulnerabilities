from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Database URL configuration (uses environment variable with SQLite fallback)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@db:5432/cisco_app")

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_size=10,            # Basic connection pooling
    max_overflow=20,         # Allow extra connections under load
    pool_pre_ping=True       # Check connections before using them
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for models
Base = declarative_base()

def get_db():
    """
    Dependency function to get DB session.
    Use this in your FastAPI route dependencies.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Initialize the database (create tables).
    Call this during application startup.
    """
    Base.metadata.create_all(bind=engine)
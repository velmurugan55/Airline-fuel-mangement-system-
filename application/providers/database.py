"""
Database provider — SQLAlchemy sync engine + session factory.
Using a sync driver (psycopg2) that is simpler to run with standard
FastAPI dependency injection. All route handlers declare async but the
DB I/O itself is synchronous (adequate for this workload size).
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from application.config import settings
import logging

logger = logging.getLogger(__name__)

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,           # verify connections before use
    pool_size=10,
    max_overflow=20,
    echo=settings.DEBUG,          # log SQL in dev mode
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def get_db():
    """
    FastAPI dependency that provides a database session per request
    and guarantees it is closed afterwards.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

"""Database configuration and connection."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
import os

from .models import Base


class Database:
    """Database manager."""

    def __init__(self, database_url: str = None):
        """Initialize database connection."""
        self.database_url = database_url or os.getenv("DATABASE_URL")

        # Create engine
        self.engine = create_engine(
            self.database_url,
            pool_pre_ping=True,
            echo=False
        )

        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def create_all(self):
        """Create all tables."""
        Base.metadata.create_all(bind=self.engine)

    def drop_all(self):
        """Drop all tables."""
        Base.metadata.drop_all(bind=self.engine)

    @contextmanager
    def get_session(self) -> Session:
        """Get database session as context manager."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_db(self):
        """Get database session (for FastAPI dependency)."""
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()


# Global database instance
db_instance = None


def get_database() -> Database:
    """Get or create global database instance."""
    global db_instance
    if db_instance is None:
        db_instance = Database()
    return db_instance

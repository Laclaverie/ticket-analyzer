from sqlalchemy.orm import Session

from persistence.base import Base
from persistence.engine import create_db_engine, create_session_factory
import persistence.models  # noqa: F401 — registers all models with Base.metadata


def create_all_tables(database_url: str) -> None:
    """Create all tables that do not yet exist. Safe to call on every startup."""
    engine = create_db_engine(database_url)
    Base.metadata.create_all(engine)


def get_session_factory(database_url: str):
    engine = create_db_engine(database_url)
    return create_session_factory(engine)

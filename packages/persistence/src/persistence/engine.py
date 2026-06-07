from pathlib import Path
from sqlalchemy import Engine, create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker
from typing import Generator

_engines: dict[str, Engine] = {}


def create_db_engine(database_url: str) -> Engine:
    """
    Return a cached SQLAlchemy engine for the given URL.
    SQLite engines are configured for single-thread usage by default.
    """
    if database_url not in _engines:
        connect_args: dict = {}
        if database_url.startswith("sqlite"):
            connect_args["check_same_thread"] = False
            url = make_url(database_url)
            database = url.database
            if database and database not in {":memory:"}:
                Path(database).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
        _engines[database_url] = create_engine(database_url, connect_args=connect_args)
    return _engines[database_url]


def create_session_factory(engine: Engine):
    """Return a sessionmaker bound to the given engine."""
    return sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_session(database_url: str) -> Generator[Session, None, None]:
    """Yield a database session and close it after use."""
    engine = create_db_engine(database_url)
    factory = create_session_factory(engine)
    session = factory()
    try:
        yield session
    finally:
        session.close()

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from api_service.main import create_app
from api_service.dependencies import get_db, get_settings
from api_service.config import Settings
from persistence.base import Base
import persistence.models  # noqa: F401


@pytest.fixture
def db_engine(tmp_path):
    engine = create_engine(
        f"sqlite:///{tmp_path}/test.db",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(db_engine) -> Session:
    factory = sessionmaker(bind=db_engine, autocommit=False, autoflush=False)
    session = factory()
    yield session
    session.close()


@pytest.fixture
def test_settings(tmp_path) -> Settings:
    return Settings(
        database_url=f"sqlite:///{tmp_path}/test.db",
        storage_path=str(tmp_path / "images"),
        api_token="",
    )


@pytest.fixture
def client(db_session: Session, test_settings: Settings) -> TestClient:
    app = create_app(test_settings)

    def override_db():
        yield db_session

    app.dependency_overrides[get_db] = override_db

    with TestClient(app) as c:
        yield c

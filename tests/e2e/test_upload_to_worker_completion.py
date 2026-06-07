import io

from fastapi.testclient import TestClient

from api_service.dependencies import get_db
from api_service.main import create_app
from api_service.config import Settings
from persistence.base import Base
from persistence.models.processing_job import ProcessingJobORM
from persistence.models.receipt_item import ReceiptItemNormalizedORM, ReceiptItemRawORM
from persistence.engine import create_db_engine, create_session_factory
import persistence.models  # noqa: F401
from worker_service.poller import JobPoller
from worker_service.processors.base import BaseProcessor
from worker_service.processors.stub_processor import StubProcessor


def test_upload_then_worker_completes_job(tmp_path):
    db_file = tmp_path / "e2e.db"
    images_dir = tmp_path / "images"

    settings = Settings(
        database_url=f"sqlite:///{db_file}",
        storage_path=str(images_dir),
        api_token="",
    )

    engine = create_db_engine(settings.database_url)
    Base.metadata.create_all(engine)

    factory = create_session_factory(engine)
    session = factory()

    app = create_app(settings)

    def override_db():
        yield session

    app.dependency_overrides[get_db] = override_db

    try:
        with TestClient(app) as client:
            response = client.post(
                "/receipts/upload",
                files={"file": ("receipt.jpg", io.BytesIO(b"fake image"), "image/jpeg")},
            )

        assert response.status_code == 201
        payload = response.json()
        job_id = payload["job_id"]

        job = session.get(ProcessingJobORM, job_id)
        assert job is not None
        assert job.status == "pending"

        poller = JobPoller(db=session, processor=StubProcessor(db=session))
        assert poller.poll_once() == 1

        session.refresh(job)
        assert job.status == "completed"

        raw_items = (
            session.query(ReceiptItemRawORM)
            .filter(ReceiptItemRawORM.receipt_id == job.receipt_id)
            .all()
        )
        normalized_items = session.query(ReceiptItemNormalizedORM).all()

        assert len(raw_items) == 1
        assert len(normalized_items) == 1
    finally:
        session.close()


def test_upload_then_retry_then_worker_completes_job(tmp_path):
    db_file = tmp_path / "e2e_retry.db"
    images_dir = tmp_path / "images"

    settings = Settings(
        database_url=f"sqlite:///{db_file}",
        storage_path=str(images_dir),
        api_token="",
    )

    engine = create_db_engine(settings.database_url)
    Base.metadata.create_all(engine)

    factory = create_session_factory(engine)
    session = factory()

    app = create_app(settings)

    def override_db():
        yield session

    app.dependency_overrides[get_db] = override_db

    class FlakyProcessor(BaseProcessor):
        def __init__(self, db_session):
            self._db = db_session
            self._calls = 0

        @property
        def name(self) -> str:
            return "flaky"

        def process(self, job_id: str) -> None:
            self._calls += 1
            if self._calls == 1:
                raise RuntimeError("transient")
            StubProcessor(db=self._db).process(job_id)

    try:
        with TestClient(app) as client:
            response = client.post(
                "/receipts/upload",
                files={"file": ("receipt.jpg", io.BytesIO(b"fake image"), "image/jpeg")},
            )

        assert response.status_code == 201
        job_id = response.json()["job_id"]

        job = session.get(ProcessingJobORM, job_id)
        assert job is not None

        poller = JobPoller(db=session, processor=FlakyProcessor(session), retry_delay_seconds=0)

        assert poller.poll_once() == 1
        session.refresh(job)
        assert job.status == "pending"
        assert job.retry_count == 1
        assert job.next_retry_at is not None

        assert poller.poll_once() == 1
        session.refresh(job)
        assert job.status == "completed"
        assert job.retry_count == 1

        raw_items = (
            session.query(ReceiptItemRawORM)
            .filter(ReceiptItemRawORM.receipt_id == job.receipt_id)
            .all()
        )
        normalized_items = session.query(ReceiptItemNormalizedORM).all()

        assert len(raw_items) == 1
        assert len(normalized_items) == 1
    finally:
        session.close()

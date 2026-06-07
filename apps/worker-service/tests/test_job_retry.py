from datetime import datetime, timedelta, timezone

from persistence.models.processing_job import ProcessingJobORM
from persistence.models.receipt import ReceiptORM
from worker_service.poller import JobPoller
from worker_service.processors.base import BaseProcessor


def _make_receipt_and_job(db_session, status="pending", retry_count=0, max_attempts=3):
    receipt = ReceiptORM(currency="EUR")
    db_session.add(receipt)
    db_session.flush()
    job = ProcessingJobORM(
        receipt_id=receipt.id,
        status=status,
        retry_count=retry_count,
        max_attempts=max_attempts,
        next_retry_at=None,
    )
    db_session.add(job)
    db_session.commit()
    return receipt, job


def test_pending_jobs_ignore_future_retry_time(db_session):
    _, job = _make_receipt_and_job(db_session, status="pending")
    job.next_retry_at = datetime.now(timezone.utc) + timedelta(minutes=5)
    db_session.commit()

    from worker_service.repositories.job_repository import JobRepository

    repo = JobRepository(db_session)
    assert repo.find_pending() == []


def test_failed_job_is_requeued_before_max_attempts(db_session):
    _, job = _make_receipt_and_job(db_session, status="pending", retry_count=0, max_attempts=3)

    class ExplodingProcessor(BaseProcessor):
        @property
        def name(self) -> str:
            return "boom"

        def process(self, job_id: str) -> None:
            raise RuntimeError("transient")

    poller = JobPoller(db=db_session, processor=ExplodingProcessor(), retry_delay_seconds=1)
    count = poller.poll_once()

    db_session.refresh(job)
    assert count == 1
    assert job.status == "pending"
    assert job.retry_count == 1
    assert job.next_retry_at is not None
    assert job.error_message == "transient"


def test_failed_job_becomes_terminal_after_max_attempts(db_session):
    _, job = _make_receipt_and_job(db_session, status="pending", retry_count=2, max_attempts=3)

    class ExplodingProcessor(BaseProcessor):
        @property
        def name(self) -> str:
            return "boom"

        def process(self, job_id: str) -> None:
            raise RuntimeError("transient")

    poller = JobPoller(db=db_session, processor=ExplodingProcessor(), retry_delay_seconds=1)
    count = poller.poll_once()

    db_session.refresh(job)
    assert count == 1
    assert job.status == "failed"
    assert job.retry_count == 2
    assert job.error_message == "transient"

import pytest
from persistence.models.receipt import ReceiptORM
from persistence.models.processing_job import ProcessingJobORM
from worker_service.poller import JobPoller
from worker_service.processors.stub_processor import StubProcessor


def _make_job(db_session, receipt, status: str = "pending") -> ProcessingJobORM:
    job = ProcessingJobORM(receipt_id=receipt.id, status=status)
    db_session.add(job)
    db_session.commit()
    return job


@pytest.fixture
def receipt(db_session) -> ReceiptORM:
    r = ReceiptORM(currency="EUR")
    db_session.add(r)
    db_session.commit()
    return r


@pytest.fixture
def poller(db_session) -> JobPoller:
    return JobPoller(db=db_session, processor=StubProcessor(db=db_session))


def test_poll_once_returns_zero_when_no_pending_jobs(poller):
    assert poller.poll_once() == 0


def test_poll_once_processes_one_pending_job(poller, db_session, receipt):
    _make_job(db_session, receipt, status="pending")
    count = poller.poll_once()
    assert count == 1


def test_poll_once_marks_job_completed(poller, db_session, receipt):
    job = _make_job(db_session, receipt, status="pending")
    poller.poll_once()
    db_session.refresh(job)
    assert job.status == "completed"


def test_poll_once_does_not_process_completed_jobs(poller, db_session, receipt):
    _make_job(db_session, receipt, status="completed")
    count = poller.poll_once()
    assert count == 0


def test_poll_once_does_not_process_failed_jobs(poller, db_session, receipt):
    _make_job(db_session, receipt, status="failed")
    count = poller.poll_once()
    assert count == 0


def test_poll_once_processes_multiple_jobs(poller, db_session, receipt):
    _make_job(db_session, receipt, status="pending")
    _make_job(db_session, receipt, status="pending")
    count = poller.poll_once()
    assert count == 2


def test_poll_once_marks_all_processed_jobs_completed(poller, db_session, receipt):
    j1 = _make_job(db_session, receipt, status="pending")
    j2 = _make_job(db_session, receipt, status="pending")
    poller.poll_once()
    db_session.refresh(j1)
    db_session.refresh(j2)
    assert j1.status == "completed"
    assert j2.status == "completed"

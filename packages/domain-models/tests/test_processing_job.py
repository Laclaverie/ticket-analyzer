import pytest
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

from domain_models.processing_job import ProcessingJob
from domain_models.enums import ProcessingStatus


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _make_job(**kwargs) -> ProcessingJob:
    now = _now()
    defaults = dict(
        id="job-1",
        receipt_id="receipt-1",
        status=ProcessingStatus.PENDING,
        error_message=None,
        retry_count=0,
        max_attempts=3,
        next_retry_at=None,
        created_at=now,
        updated_at=now,
    )
    return ProcessingJob(**{**defaults, **kwargs})


def test_processing_job_creation_succeeds():
    job = _make_job()
    assert job.id == "job-1"
    assert job.status == ProcessingStatus.PENDING


def test_processing_job_is_immutable():
    job = _make_job()
    with pytest.raises(FrozenInstanceError):
        job.status = ProcessingStatus.COMPLETED  # type: ignore[misc]


def test_processing_job_rejects_empty_id():
    with pytest.raises(ValueError, match="id"):
        _make_job(id="")


def test_processing_job_rejects_empty_receipt_id():
    with pytest.raises(ValueError, match="receipt_id"):
        _make_job(receipt_id="")


def test_processing_job_accepts_error_message():
    job = _make_job(status=ProcessingStatus.FAILED, error_message="OCR failed")
    assert job.error_message == "OCR failed"
    assert job.status == ProcessingStatus.FAILED


def test_processing_job_accepts_none_error_message():
    job = _make_job(error_message=None)
    assert job.error_message is None

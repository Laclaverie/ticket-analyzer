from datetime import datetime, timezone

from domain_models.enums import ProcessingStatus
from domain_models.processing_job import ProcessingJob


def test_processing_job_retry_fields_are_preserved():
    now = datetime.now(timezone.utc)
    job = ProcessingJob(
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
    assert job.retry_count == 0
    assert job.max_attempts == 3
    assert job.next_retry_at is None


def test_processing_job_rejects_negative_retry_count():
    now = datetime.now(timezone.utc)
    try:
        ProcessingJob(
            id="job-1",
            receipt_id="receipt-1",
            status=ProcessingStatus.PENDING,
            error_message=None,
            retry_count=-1,
            max_attempts=3,
            next_retry_at=None,
            created_at=now,
            updated_at=now,
        )
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "retry_count" in str(exc)

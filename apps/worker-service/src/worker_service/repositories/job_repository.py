import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from domain_models.enums import ProcessingStatus
from domain_models.processing_job import ProcessingJob
from persistence.models.processing_job import ProcessingJobORM


class JobRepository:
    """
    Worker-side job repository.
    Reads pending jobs and writes status transitions.
    Does NOT commit — JobPoller owns all transaction boundaries.
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    def find_pending(
        self,
        limit: int = 10,
        now: Optional[datetime] = None,
    ) -> list[ProcessingJob]:
        current_time = now or datetime.now(timezone.utc)
        orms = (
            self._db.query(ProcessingJobORM)
            .filter(ProcessingJobORM.status == ProcessingStatus.PENDING.value)
            .filter(
                (ProcessingJobORM.next_retry_at.is_(None))
                | (ProcessingJobORM.next_retry_at <= current_time)
            )
            .limit(limit)
            .all()
        )
        return [self._to_domain(o) for o in orms]

    def mark_completed(self, job_id: str) -> None:
        self._update_status(job_id, ProcessingStatus.COMPLETED)

    def mark_in_progress(self, job_id: str) -> None:
        self._update_status(job_id, ProcessingStatus.IN_PROGRESS)

    def mark_failed(self, job_id: str, error_message: str) -> None:
        self._update_status(job_id, ProcessingStatus.FAILED, error_message)

    def schedule_retry(
        self,
        job_id: str,
        error_message: str,
        next_retry_at: datetime,
    ) -> None:
        job = self._db.get(ProcessingJobORM, job_id)
        if job:
            job.status = ProcessingStatus.PENDING.value
            job.error_message = error_message
            job.retry_count += 1
            job.next_retry_at = next_retry_at
            job.updated_at = datetime.now(timezone.utc)

    def _update_status(
        self,
        job_id: str,
        status: ProcessingStatus,
        error_message: Optional[str] = None,
    ) -> None:
        job = self._db.get(ProcessingJobORM, job_id)
        if job:
            job.status = status.value
            job.error_message = error_message
            if status in {ProcessingStatus.COMPLETED, ProcessingStatus.FAILED}:
                job.next_retry_at = None
            job.updated_at = datetime.now(timezone.utc)

    @staticmethod
    def _to_domain(orm: ProcessingJobORM) -> ProcessingJob:
        next_retry_at = orm.next_retry_at
        if next_retry_at is not None and next_retry_at.tzinfo is None:
            next_retry_at = next_retry_at.replace(tzinfo=timezone.utc)

        return ProcessingJob(
            id=orm.id,
            receipt_id=orm.receipt_id,
            status=ProcessingStatus(orm.status),
            error_message=orm.error_message,
            retry_count=orm.retry_count,
            max_attempts=orm.max_attempts,
            next_retry_at=next_retry_at,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )

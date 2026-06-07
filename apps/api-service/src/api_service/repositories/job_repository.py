import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from domain_models.enums import ProcessingStatus
from domain_models.processing_job import ProcessingJob
from persistence.models.processing_job import ProcessingJobORM


class JobRepository:
    """
    Translates between ProcessingJobORM and domain objects.
    Used by api-service to enqueue jobs after upload.
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    def create(self, receipt_id: str) -> ProcessingJob:
        now = datetime.now(timezone.utc)
        orm = ProcessingJobORM(
            id=str(uuid.uuid4()),
            receipt_id=receipt_id,
            status=ProcessingStatus.PENDING.value,
            created_at=now,
            updated_at=now,
        )
        self._db.add(orm)
        self._db.flush()
        return self._to_domain(orm)

    def find_by_id(self, job_id: str) -> Optional[ProcessingJob]:
        orm = self._db.get(ProcessingJobORM, job_id)
        return self._to_domain(orm) if orm else None

    @staticmethod
    def _to_domain(orm: ProcessingJobORM) -> ProcessingJob:
        return ProcessingJob(
            id=orm.id,
            receipt_id=orm.receipt_id,
            status=ProcessingStatus(orm.status),
            error_message=orm.error_message,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )

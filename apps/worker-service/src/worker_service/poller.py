import logging
import time
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from worker_service.processors.base import BaseProcessor
from worker_service.repositories.job_repository import JobRepository
from persistence.models.processing_job import ProcessingJobORM

logger = logging.getLogger(__name__)


class JobPoller:
    """
    Polls the database for PENDING jobs and dispatches them to a BaseProcessor.

    Template Method: the fixed lifecycle (find → process → mark done/failed) is
    defined here; the variable step (the actual processing) is delegated to the
    injected processor strategy.
    """

    def __init__(
        self,
        db: Session,
        processor: BaseProcessor,
        poll_interval_seconds: float = 5.0,
        batch_size: int = 10,
        retry_delay_seconds: float = 30.0,
    ) -> None:
        self._db = db
        self._processor = processor
        self._poll_interval = poll_interval_seconds
        self._batch_size = batch_size
        self._retry_delay_seconds = retry_delay_seconds
        self._job_repo = JobRepository(db)

    def poll_once(self) -> int:
        """
        Process one batch of pending jobs.
        Returns the number of jobs dispatched in this pass.
        """
        jobs = self._job_repo.find_pending(limit=self._batch_size)

        for job in jobs:
            try:
                self._job_repo.mark_in_progress(job.id)
                self._db.commit()

                self._processor.process(job.id)
                self._job_repo.mark_completed(job.id)
                self._db.commit()
                logger.info("Job %s completed by %s.", job.id, self._processor.name)
            except Exception as exc:
                self._db.rollback()
                current = self._db.get(ProcessingJobORM, job.id)
                if current and current.retry_count + 1 < current.max_attempts:
                    retry_at = datetime.now(timezone.utc) + timedelta(seconds=self._retry_delay_seconds)
                    self._job_repo.schedule_retry(job.id, str(exc), retry_at)
                    logger.warning(
                        "Job %s failed and will retry at %s (%s/%s): %s",
                        job.id,
                        retry_at.isoformat(),
                        current.retry_count + 1,
                        current.max_attempts,
                        exc,
                    )
                else:
                    self._job_repo.mark_failed(job.id, str(exc))
                    logger.exception("Job %s failed permanently: %s", job.id, exc)
                self._db.commit()

        return len(jobs)

    def run(self) -> None:
        """Run the polling loop indefinitely."""
        logger.info("Worker started with processor: %s", self._processor.name)
        while True:
            processed = self.poll_once()
            if processed == 0:
                time.sleep(self._poll_interval)

import logging

from sqlalchemy.orm import Session

from worker_service.processors.base import BaseProcessor

logger = logging.getLogger(__name__)


class StubProcessor(BaseProcessor):
    """
    Phase 0 no-op processor.

    Does not perform any real work. Its purpose is to verify that the full
    ingestion → job → processing → completion pipeline is wired together.

    Will be replaced by OcrProcessor in Phase 1. Open for extension: subclass
    BaseProcessor, register the new processor in main.py. No other code changes needed.
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    @property
    def name(self) -> str:
        return "stub"

    def process(self, job_id: str) -> None:
        # Phase 0: no-op. Status transitions are managed by JobPoller.
        logger.info("StubProcessor: Phase 0 no-op for job %s.", job_id)

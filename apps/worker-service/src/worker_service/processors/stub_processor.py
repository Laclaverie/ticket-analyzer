import logging
from pathlib import Path

from sqlalchemy.orm import Session

from persistence.models.processing_job import ProcessingJobORM
from persistence.models.receipt import ReceiptORM
from persistence.models.receipt_item import ReceiptItemNormalizedORM, ReceiptItemRawORM

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
        job = self._db.get(ProcessingJobORM, job_id)
        if not job:
            logger.info("StubProcessor: job %s not found, skipping.", job_id)
            return

        receipt = self._db.get(ReceiptORM, job.receipt_id)
        if not receipt:
            raise ValueError(f"Receipt {job.receipt_id} not found for job {job_id}")

        self._replace_extracted_items(receipt)
        logger.info("StubProcessor: wrote placeholder extraction output for job %s.", job_id)

    def _replace_extracted_items(self, receipt: ReceiptORM) -> None:
        existing_raw_items = (
            self._db.query(ReceiptItemRawORM)
            .filter(ReceiptItemRawORM.receipt_id == receipt.id)
            .all()
        )
        existing_raw_ids = [item.id for item in existing_raw_items]
        if existing_raw_ids:
            existing_normalized_items = (
                self._db.query(ReceiptItemNormalizedORM)
                .filter(ReceiptItemNormalizedORM.receipt_item_raw_id.in_(existing_raw_ids))
                .all()
            )
            for item in existing_normalized_items:
                self._db.delete(item)

        for raw in existing_raw_items:
            self._db.delete(raw)

        image_name = "receipt"
        if receipt.images:
            image_name = Path(receipt.images[0].file_path).stem

        raw_item = ReceiptItemRawORM(
            receipt_id=receipt.id,
            raw_text=f"item:{image_name}",
            line_number=1,
        )
        self._db.add(raw_item)
        self._db.flush()

        normalized = ReceiptItemNormalizedORM(
            receipt_item_raw_id=raw_item.id,
            normalized_name=image_name.replace("_", " ").strip() or "unknown item",
            quantity=None,
            unit_price=None,
            line_total=None,
            category_id=None,
            confidence=0.1,
            classification_origin="rule",
        )
        self._db.add(normalized)

from pathlib import Path

from sqlalchemy.orm import Session

from persistence.models.processing_job import ProcessingJobORM
from persistence.models.receipt import ReceiptORM
from persistence.models.receipt_item import ReceiptItemNormalizedORM, ReceiptItemRawORM

from worker_service.processors.base import BaseProcessor
from worker_service.processors.ocr_client import BaseOcrClient


class OcrProcessor(BaseProcessor):
    """OCR-backed processor that persists raw and normalized placeholders."""

    def __init__(self, db: Session, ocr_client: BaseOcrClient) -> None:
        self._db = db
        self._ocr_client = ocr_client

    @property
    def name(self) -> str:
        return "ocr"

    def process(self, job_id: str) -> None:
        job = self._db.get(ProcessingJobORM, job_id)
        if not job:
            return

        receipt = self._db.get(ReceiptORM, job.receipt_id)
        if not receipt:
            raise ValueError(f"Receipt {job.receipt_id} not found for job {job_id}")
        if not receipt.images:
            raise ValueError(f"No image found for receipt {receipt.id}")

        image_path = receipt.images[0].file_path
        text = self._ocr_client.extract_text(image_path)
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if not lines:
            lines = [Path(image_path).stem or "unreadable receipt"]

        self._replace_extracted_items(receipt.id, lines)

    def _replace_extracted_items(self, receipt_id: str, lines: list[str]) -> None:
        existing_raw_items = (
            self._db.query(ReceiptItemRawORM)
            .filter(ReceiptItemRawORM.receipt_id == receipt_id)
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
        self._db.flush()

        for index, line in enumerate(lines, start=1):
            raw_item = ReceiptItemRawORM(
                receipt_id=receipt_id,
                raw_text=line,
                line_number=index,
            )
            self._db.add(raw_item)
            self._db.flush()

            normalized = ReceiptItemNormalizedORM(
                receipt_item_raw_id=raw_item.id,
                normalized_name=line.lower(),
                quantity=None,
                unit_price=None,
                line_total=None,
                category_id=None,
                confidence=0.5,
                classification_origin="model",
            )
            self._db.add(normalized)

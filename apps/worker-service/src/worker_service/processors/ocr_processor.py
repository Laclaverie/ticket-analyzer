from pathlib import Path
import logging

from sqlalchemy.orm import Session

from parsing_core.parser import ReceiptLineParser
from parsing_core.detector import StoreDetector
from persistence.models.processing_job import ProcessingJobORM
from persistence.models.receipt import ReceiptORM
from persistence.models.receipt_item import ReceiptItemNormalizedORM, ReceiptItemRawORM
from taxonomy_core.classifier import BaseClassifier

from worker_service.processors.base import BaseProcessor
from worker_service.processors.ocr_client import BaseOcrClient

logger = logging.getLogger(__name__)


class OcrProcessor(BaseProcessor):
    """OCR-backed processor that persists raw and normalized items with category assignment."""

    def __init__(
        self,
        db: Session,
        ocr_client: BaseOcrClient,
        classifier: BaseClassifier,
        store_detector: StoreDetector = StoreDetector(),
    ) -> None:
        self._db = db
        self._ocr_client = ocr_client
        self._classifier = classifier
        self._store_detector = store_detector

    @property
    def name(self) -> str:
        return "ocr"

    def process(self, job_id: str) -> None:
        job = self._db.get(ProcessingJobORM, job_id)
        if not job:
            logger.error("Job %s not found in database.", job_id)
            return

        receipt = self._db.get(ReceiptORM, job.receipt_id)
        if not receipt:
            logger.error("Receipt %s not found for job %s.", job.receipt_id, job_id)
            raise ValueError(f"Receipt {job.receipt_id} not found for job {job_id}")

        if not receipt.images:
            logger.error("No image found for receipt %s.", receipt.id)
            raise ValueError(f"No image found for receipt {receipt.id}")

        image_path = receipt.images[0].file_path
        logger.info("Processing job %s for receipt %s using image: %s", job_id, receipt.id, image_path)

        # Ensure image path is readable
        if not Path(image_path).exists():
             logger.warning("Image path %s does not exist. This might be due to shared storage discrepancy.", image_path)

        text = self._ocr_client.extract_text(image_path)
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        if not lines:
            logger.warning("OCR returned no text. Using fallback.")
            lines = [Path(image_path).stem or "unreadable receipt"]

        logger.info("Extracted %d lines of text from image.", len(lines))

        # Detect store and create specialized parser
        store_type = self._store_detector.detect(lines)
        logger.info("Detected store type: %s", store_type)

        line_parser = ReceiptLineParser(store_type=store_type)

        self._replace_extracted_items(receipt.id, lines, line_parser)
        logger.info("Successfully persisted %d lines for receipt %s.", len(lines), receipt.id)

    def _replace_extracted_items(self, receipt_id: str, lines: list[str], line_parser: ReceiptLineParser) -> None:
        existing_raw_items = (
            self._db.query(ReceiptItemRawORM)
            .filter(ReceiptItemRawORM.receipt_id == receipt_id)
            .all()
        )
        existing_raw_ids = [item.id for item in existing_raw_items]

        if existing_raw_ids:
            logger.debug("Deleting %d existing items for receipt %s.", len(existing_raw_ids), receipt_id)
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

        parsed_count = 0
        for index, line in enumerate(lines, start=1):
            raw_item = ReceiptItemRawORM(
                receipt_id=receipt_id,
                raw_text=line,
                line_number=index,
            )
            self._db.add(raw_item)
            self._db.flush()

            parsed = line_parser.parse_line(line)
            classification = self._classifier.classify(parsed.normalized_name)

            normalized = ReceiptItemNormalizedORM(
                receipt_item_raw_id=raw_item.id,
                normalized_name=parsed.normalized_name,
                quantity=parsed.quantity,
                unit_price=parsed.unit_price,
                line_total=parsed.line_total,
                category_id=classification.category_id,
                confidence=classification.confidence,
                classification_origin=classification.origin,
            )
            self._db.add(normalized)
            if parsed.line_total is not None:
                parsed_count += 1

        logger.info("Normalized %d items from %d lines.", parsed_count, len(lines))

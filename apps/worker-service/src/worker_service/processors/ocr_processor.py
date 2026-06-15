from pathlib import Path
import logging
import csv

from sqlalchemy.orm import Session

from parsing_core.parser import ReceiptLineParser
from parsing_core.detector import StoreDetector
from persistence.models.processing_job import ProcessingJobORM
from persistence.models.receipt import ReceiptORM
from persistence.models.receipt_item import ReceiptItemNormalizedORM, ReceiptItemRawORM
from taxonomy_core.classifier import BaseClassifier

from worker_service.processors.base import BaseProcessor
from worker_service.processors.ocr_client import BaseOcrClient
from worker_service.processors.preprocessor import BaseImagePreprocessor, NoOpPreprocessor
from worker_service.processors.layout_segmenter import BaseLayoutSegmenter, NoOpLayoutSegmenter

logger = logging.getLogger(__name__)


class OcrProcessor(BaseProcessor):
    """OCR-backed processor that persists raw and normalized items with category assignment."""

    def __init__(
        self,
        db: Session,
        ocr_client: BaseOcrClient,
        classifier: BaseClassifier,
        store_detector: StoreDetector = StoreDetector(),
        preprocessor: BaseImagePreprocessor = NoOpPreprocessor(),
        layout_segmenter: BaseLayoutSegmenter = NoOpLayoutSegmenter(),
        debug_mode: bool = False,
    ) -> None:
        self._db = db
        self._ocr_client = ocr_client
        self._classifier = classifier
        self._store_detector = store_detector
        self._preprocessor = preprocessor
        self._layout_segmenter = layout_segmenter
        self._debug_mode = debug_mode

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

        # Pre-process image (deskew, threshold, etc.)
        processed_image_path = self._preprocessor.process(image_path, debug=self._debug_mode)
        if processed_image_path != image_path:
            logger.info("Using pre-processed image: %s", processed_image_path)

        # Layout Segmentation
        regions = self._layout_segmenter.segment(processed_image_path)

        header_regions = [r for r in regions if r.label == "header"]
        body_regions = [r for r in regions if r.label == "body"]
        line_item_regions = [r for r in regions if r.label == "line_item"]

        # If no body or line_item regions detected, use all regions as body (fallback)
        if not body_regions and not line_item_regions and not header_regions:
            body_regions = regions

        # Sort regions by their vertical position (y1) to ensure text order is preserved
        header_regions.sort(key=lambda r: r.bbox[1])
        body_regions.sort(key=lambda r: r.bbox[1])
        line_item_regions.sort(key=lambda r: r.bbox[1])

        # Extract text from regions
        header_text = ""
        for region in header_regions:
            header_text += self._ocr_client.extract_text(str(region.image_path)) + "\n"

        body_lines = []

        # If we have specific line items, OCR each one individually (most robust)
        if line_item_regions:
            logger.info("Processing %d line_item regions.", len(line_item_regions))
            for region in line_item_regions:
                line_text = self._ocr_client.extract_text(str(region.image_path)).strip()
                if line_text:
                    body_lines.append(line_text)
        else:
            # Fallback to whole body segments
            for region in body_regions:
                region_text = self._ocr_client.extract_text(str(region.image_path))
                body_lines.extend([line.strip() for line in region_text.splitlines() if line.strip()])

        # If layout segmentation returned nothing or body_lines is empty, fallback to full image
        if not body_lines:
            logger.warning("No text extracted from layout regions. Falling back to full image OCR.")
            full_text = self._ocr_client.extract_text(processed_image_path)
            body_lines = [line.strip() for line in full_text.splitlines() if line.strip()]

        if not body_lines:
            logger.warning("OCR returned no text. Using fallback.")
            body_lines = [Path(image_path).stem or "unreadable receipt"]

        logger.info("Extracted %d lines of text from body regions.", len(body_lines))

        # Detect store using header text if available, otherwise use body lines
        if header_text:
            store_type = self._store_detector.detect(header_text.splitlines())
        else:
            store_type = self._store_detector.detect(body_lines)

        logger.info("Detected store type: %s", store_type)

        line_parser = ReceiptLineParser(store_type=store_type)

        dump_data = self._replace_extracted_items(receipt.id, body_lines, line_parser)

        if self._debug_mode and dump_data:
            receipt_dir = Path(image_path).parent
            csv_path = receipt_dir / "parsing_dump.csv"
            logger.info("Debug mode: Dumping parsing results to %s", csv_path)
            try:
                with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=dump_data[0].keys())
                    writer.writeheader()
                    writer.writerows(dump_data)
            except Exception as e:
                logger.error("Failed to write parsing dump CSV: %s", e)

        logger.info("Successfully persisted %d lines for receipt %s.", len(body_lines), receipt.id)

    def _replace_extracted_items(self, receipt_id: str, lines: list[str], line_parser: ReceiptLineParser) -> list[dict]:
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
        dump_data = []
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
            if self._debug_mode:
                dump_data.append({
                    "line_number": index,
                    "raw_text": line,
                    "normalized_name": parsed.normalized_name,
                    "quantity": parsed.quantity,
                    "unit_price": parsed.unit_price,
                    "line_total": parsed.line_total,
                    "category_id": classification.category_id,
                })

            if parsed.line_total is not None:
                parsed_count += 1

        logger.info("Normalized %d items from %d lines.", parsed_count, len(lines))
        return dump_data

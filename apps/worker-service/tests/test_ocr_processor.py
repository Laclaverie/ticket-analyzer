from persistence.models.processing_job import ProcessingJobORM
from persistence.models.receipt import ReceiptImageORM, ReceiptORM
from persistence.models.receipt_item import ReceiptItemNormalizedORM, ReceiptItemRawORM
from parsing_core.parser import ReceiptLineParser
from worker_service.processors.ocr_client import BaseOcrClient
from worker_service.processors.ocr_processor import OcrProcessor


class FakeOcrClient(BaseOcrClient):
    def __init__(self, text: str) -> None:
        self._text = text

    def extract_text(self, image_path: str) -> str:
        return self._text


def _make_receipt_with_job(db_session, image_path: str = "/tmp/receipt.jpg") -> ProcessingJobORM:
    receipt = ReceiptORM(currency="EUR")
    db_session.add(receipt)
    db_session.flush()

    image = ReceiptImageORM(receipt_id=receipt.id, file_path=image_path, file_hash="hash")
    db_session.add(image)

    job = ProcessingJobORM(receipt_id=receipt.id, status="pending")
    db_session.add(job)
    db_session.commit()
    return job


def test_ocr_processor_name(db_session):
    processor = OcrProcessor(db_session, FakeOcrClient("milk"), ReceiptLineParser())
    assert processor.name == "ocr"


def test_ocr_processor_persists_rows_from_lines(db_session):
    job = _make_receipt_with_job(db_session)
    processor = OcrProcessor(
        db_session,
        FakeOcrClient("Milk 2.99\nTomato 2 x 1.49 2.98\n"),
        ReceiptLineParser(),
    )

    processor.process(job.id)
    db_session.flush()

    raw_items = (
        db_session.query(ReceiptItemRawORM)
        .filter(ReceiptItemRawORM.receipt_id == job.receipt_id)
        .order_by(ReceiptItemRawORM.line_number)
        .all()
    )
    normalized_items = (
        db_session.query(ReceiptItemNormalizedORM)
        .join(ReceiptItemRawORM, ReceiptItemRawORM.id == ReceiptItemNormalizedORM.receipt_item_raw_id)
        .filter(ReceiptItemRawORM.receipt_id == job.receipt_id)
        .all()
    )

    assert len(raw_items) == 2
    assert raw_items[0].raw_text == "Milk 2.99"
    assert raw_items[1].raw_text == "Tomato 2 x 1.49 2.98"
    assert len(normalized_items) == 2
    milk_item = next(item for item in normalized_items if item.normalized_name == "milk")
    tomato_item = next(item for item in normalized_items if item.normalized_name == "tomato")
    assert str(milk_item.line_total) == "2.99"
    assert str(milk_item.quantity) == "1.000"
    assert str(milk_item.unit_price) == "2.99"
    assert str(tomato_item.line_total) == "2.98"
    assert str(tomato_item.quantity) == "2.000"
    assert str(tomato_item.unit_price) == "1.49"


def test_ocr_processor_uses_fallback_when_text_empty(db_session):
    job = _make_receipt_with_job(db_session, image_path="/tmp/costco-ticket.jpg")
    processor = OcrProcessor(db_session, FakeOcrClient("\n\n"), ReceiptLineParser())

    processor.process(job.id)
    db_session.flush()

    raw_items = (
        db_session.query(ReceiptItemRawORM)
        .filter(ReceiptItemRawORM.receipt_id == job.receipt_id)
        .all()
    )

    assert len(raw_items) == 1
    assert raw_items[0].raw_text == "costco-ticket"


def test_ocr_processor_raises_when_image_missing(db_session):
    receipt = ReceiptORM(currency="EUR")
    db_session.add(receipt)
    db_session.flush()
    job = ProcessingJobORM(receipt_id=receipt.id, status="pending")
    db_session.add(job)
    db_session.commit()

    processor = OcrProcessor(db_session, FakeOcrClient("any"), ReceiptLineParser())

    try:
        processor.process(job.id)
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "No image found" in str(exc)

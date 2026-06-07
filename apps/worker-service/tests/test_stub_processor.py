from unittest.mock import MagicMock

from worker_service.processors.stub_processor import StubProcessor
from persistence.models.receipt_item import ReceiptItemNormalizedORM, ReceiptItemRawORM


def test_stub_processor_name():
    processor = StubProcessor(db=MagicMock())
    assert processor.name == "stub"


def test_stub_processor_process_does_not_raise_for_known_job(db_session):
    from persistence.models.receipt import ReceiptORM
    from persistence.models.receipt import ReceiptImageORM
    from persistence.models.processing_job import ProcessingJobORM

    receipt = ReceiptORM(currency="EUR")
    db_session.add(receipt)
    db_session.flush()

    job = ProcessingJobORM(receipt_id=receipt.id, status="pending")
    image = ReceiptImageORM(receipt_id=receipt.id, file_path="/tmp/example_receipt.jpg", file_hash="abc")
    db_session.add(image)
    db_session.add(job)
    db_session.commit()

    processor = StubProcessor(db=db_session)
    processor.process(job.id)  # must not raise


def test_stub_processor_process_does_not_raise_for_unknown_job(db_session):
    processor = StubProcessor(db=db_session)
    processor.process("nonexistent-job-id")  # must not raise


def test_stub_processor_does_not_change_job_status(db_session):
    """Status transitions are the poller's job, not the processor's."""
    from persistence.models.receipt import ReceiptORM
    from persistence.models.processing_job import ProcessingJobORM

    receipt = ReceiptORM(currency="EUR")
    db_session.add(receipt)
    db_session.flush()

    job = ProcessingJobORM(receipt_id=receipt.id, status="pending")
    db_session.add(job)
    db_session.commit()

    processor = StubProcessor(db=db_session)
    processor.process(job.id)

    db_session.refresh(job)
    assert job.status == "pending"


def test_stub_processor_writes_raw_and_normalized_items(db_session):
    from persistence.models.receipt import ReceiptORM, ReceiptImageORM
    from persistence.models.processing_job import ProcessingJobORM

    receipt = ReceiptORM(currency="EUR")
    db_session.add(receipt)
    db_session.flush()

    db_session.add(
        ReceiptImageORM(
            receipt_id=receipt.id,
            file_path="/tmp/banana_milk.jpg",
            file_hash="abc",
        )
    )
    job = ProcessingJobORM(receipt_id=receipt.id, status="pending")
    db_session.add(job)
    db_session.commit()

    processor = StubProcessor(db=db_session)
    processor.process(job.id)
    db_session.flush()

    raw_items = (
        db_session.query(ReceiptItemRawORM)
        .filter(ReceiptItemRawORM.receipt_id == receipt.id)
        .all()
    )
    normalized_items = db_session.query(ReceiptItemNormalizedORM).all()

    assert len(raw_items) == 1
    assert raw_items[0].raw_text == "item:banana_milk"
    assert len(normalized_items) == 1
    assert normalized_items[0].normalized_name == "banana milk"


def test_stub_processor_is_idempotent_for_same_receipt(db_session):
    from persistence.models.receipt import ReceiptORM
    from persistence.models.processing_job import ProcessingJobORM

    receipt = ReceiptORM(currency="EUR")
    db_session.add(receipt)
    db_session.flush()

    job = ProcessingJobORM(receipt_id=receipt.id, status="pending")
    db_session.add(job)
    db_session.commit()

    processor = StubProcessor(db=db_session)
    processor.process(job.id)
    processor.process(job.id)
    db_session.flush()

    raw_items = (
        db_session.query(ReceiptItemRawORM)
        .filter(ReceiptItemRawORM.receipt_id == receipt.id)
        .all()
    )
    raw_ids = [item.id for item in raw_items]
    normalized_items = (
        db_session.query(ReceiptItemNormalizedORM)
        .filter(ReceiptItemNormalizedORM.receipt_item_raw_id.in_(raw_ids))
        .all()
    )

    assert len(raw_items) == 1
    assert len(normalized_items) == 1

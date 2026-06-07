from unittest.mock import MagicMock

from worker_service.processors.stub_processor import StubProcessor


def test_stub_processor_name():
    processor = StubProcessor(db=MagicMock())
    assert processor.name == "stub"


def test_stub_processor_process_does_not_raise_for_known_job(db_session):
    from persistence.models.receipt import ReceiptORM
    from persistence.models.processing_job import ProcessingJobORM

    receipt = ReceiptORM(currency="EUR")
    db_session.add(receipt)
    db_session.flush()

    job = ProcessingJobORM(receipt_id=receipt.id, status="pending")
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

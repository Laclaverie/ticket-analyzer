from worker_service.config import Settings
from worker_service.processor_factory import create_processor
from worker_service.processors.ocr_processor import OcrProcessor
from worker_service.processors.stub_processor import StubProcessor


def test_create_processor_returns_stub(db_session):
    settings = Settings(processor_kind="stub")
    processor = create_processor(db_session, settings)
    assert isinstance(processor, StubProcessor)


def test_create_processor_returns_ocr(db_session):
    settings = Settings(processor_kind="ocr")
    processor = create_processor(db_session, settings)
    assert isinstance(processor, OcrProcessor)


def test_create_processor_is_case_insensitive(db_session):
    settings = Settings(processor_kind=" OCR ")
    processor = create_processor(db_session, settings)
    assert isinstance(processor, OcrProcessor)


def test_create_processor_raises_on_unknown_kind(db_session):
    settings = Settings(processor_kind="unknown")
    try:
        create_processor(db_session, settings)
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "Unsupported processor kind" in str(exc)

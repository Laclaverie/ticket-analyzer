from sqlalchemy.orm import Session

from parsing_core.parser import ReceiptLineParser
from worker_service.processors.base import BaseProcessor
from worker_service.processors.ocr_client import AutoOcrClient
from worker_service.processors.ocr_processor import OcrProcessor
from worker_service.processors.stub_processor import StubProcessor


def create_processor(db: Session, processor_kind: str) -> BaseProcessor:
    kind = processor_kind.strip().lower()
    if kind == "stub":
        return StubProcessor(db)
    if kind == "ocr":
        return OcrProcessor(db, AutoOcrClient(), ReceiptLineParser())
    raise ValueError(f"Unsupported processor kind: {processor_kind}")

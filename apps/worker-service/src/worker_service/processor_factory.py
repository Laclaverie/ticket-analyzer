from sqlalchemy.orm import Session

from taxonomy_core.keyword_classifier import KeywordClassifier
from taxonomy_core.loader import TaxonomyLoader
from worker_service.config import Settings
from worker_service.processors.base import BaseProcessor
from worker_service.processors.ocr_client import AutoOcrClient
from worker_service.processors.ocr_processor import OcrProcessor
from worker_service.processors.stub_processor import StubProcessor


def create_processor(db: Session, settings: Settings) -> BaseProcessor:
    kind = settings.processor_kind.strip().lower()
    if kind == "stub":
        return StubProcessor(db)
    if kind == "ocr":
        nodes = TaxonomyLoader.load_default()
        classifier = KeywordClassifier(nodes)
        # OcrProcessor now handles its own StoreDetector and ReceiptLineParser internally
        ocr_client = AutoOcrClient(tesseract_cmd=settings.tesseract_cmd)
        return OcrProcessor(db, ocr_client, classifier)
    raise ValueError(f"Unsupported processor kind: {settings.processor_kind}")

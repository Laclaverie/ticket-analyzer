from sqlalchemy.orm import Session

from taxonomy_core.keyword_classifier import KeywordClassifier
from taxonomy_core.loader import TaxonomyLoader
from worker_service.config import Settings
from worker_service.processors.base import BaseProcessor
from worker_service.processors.layout_segmenter import NoOpLayoutSegmenter, YoloLayoutSegmenter
from worker_service.processors.ocr_client import AutoOcrClient, DonutOcrClient
from worker_service.processors.ocr_processor import OcrProcessor
from worker_service.processors.preprocessor import (
    CopyStep,
    GrayscaleStep,
    NoOpPreprocessor,
    PipelinePreprocessor,
    RescaleStep,
    ThresholdStep,
    YoloDetectionStep,
)
from worker_service.processors.stub_processor import StubProcessor


def create_processor(db: Session, settings: Settings) -> BaseProcessor:
    kind = settings.processor_kind.strip().lower()
    if kind == "stub":
        return StubProcessor(db)
    if kind == "ocr":
        nodes = TaxonomyLoader.load_default()
        classifier = KeywordClassifier(nodes)

        # Build OCR client
        if settings.ocr_client_kind == "donut":
            ocr_client = DonutOcrClient()
        else:
            ocr_client = AutoOcrClient(tesseract_cmd=settings.tesseract_cmd)

        # Build preprocessing pipeline
        steps = []
        if settings.yolo_enabled and settings.use_yolo_pipeline:
            # ONLY YOLO segmentation
            steps.append(YoloDetectionStep(
                model_path=settings.yolo_model_path,
                confidence=settings.yolo_confidence
            ))
        else:
            # Fallback or legacy pipeline
            if settings.yolo_enabled:
                steps.append(YoloDetectionStep(
                    model_path=settings.yolo_model_path,
                    confidence=settings.yolo_confidence
                ))

            # Advanced preprocessing pipeline: Grayscale -> Threshold -> Rescale
            steps.extend([
                GrayscaleStep(),
                ThresholdStep(),
                RescaleStep(min_width=2000),
            ])

        preprocessor = PipelinePreprocessor(steps=steps)

        if settings.layout_segmentation_enabled:
            layout_segmenter = YoloLayoutSegmenter(
                model_path=settings.yolo_layout_model_path,
                confidence=settings.yolo_layout_confidence
            )
        else:
            layout_segmenter = NoOpLayoutSegmenter()

        return OcrProcessor(
            db,
            ocr_client,
            classifier,
            preprocessor=preprocessor,
            layout_segmenter=layout_segmenter,
            debug_mode=settings.debug_preprocessor,
        )
    raise ValueError(f"Unsupported processor kind: {settings.processor_kind}")

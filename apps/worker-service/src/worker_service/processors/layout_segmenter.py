import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import cv2
from persistence.config_utils import find_repo_root

logger = logging.getLogger(__name__)

@dataclass
class LayoutRegion:
    label: str  # 'header', 'body', 'footer', 'line_item'
    image_path: Path
    confidence: float
    bbox: List[int]  # [x1, y1, x2, y2]

class BaseLayoutSegmenter(ABC):
    """Abstract base class for segmenting a receipt into regions (Header, Body, Footer)."""

    @abstractmethod
    def segment(self, image_path: str) -> List[LayoutRegion]:
        """
        Segments the image at the given path into distinct regions.
        Returns a list of LayoutRegion objects.
        """
        pass

class NoOpLayoutSegmenter(BaseLayoutSegmenter):
    """Returns the whole image as a single 'body' region."""
    def segment(self, image_path: str) -> List[LayoutRegion]:
        return [
            LayoutRegion(
                label="body",
                image_path=Path(image_path),
                confidence=1.0,
                bbox=[0, 0, 0, 0]
            )
        ]

class YoloLayoutSegmenter(BaseLayoutSegmenter):
    """
    Uses a YOLO model to segment the receipt into 'header', 'body', and 'footer' regions.
    """
    def __init__(self, model_path: str, confidence: float = 0.45) -> None:
        self._model_path = model_path
        self._confidence = confidence
        self._model = None

    def _get_model(self):
        if self._model is None:
            model_path = Path(self._model_path)
            if not model_path.is_absolute():
                model_path = find_repo_root() / self._model_path

            try:
                from ultralytics import YOLO
                self._model = YOLO(str(model_path))
            except ImportError:
                logger.error("ultralytics library not found. YOLO layout segmentation will be skipped.")
                raise ImportError("Please install ultralytics to use YoloLayoutSegmenter.")
            except Exception as e:
                logger.error("Failed to load YOLO model from %s: %s", self._model_path, e)
                raise
        return self._model

    def segment(self, image_path: str) -> List[LayoutRegion]:
        model_path = Path(self._model_path)
        if not model_path.is_absolute():
            model_path = find_repo_root() / self._model_path

        if not model_path.exists():
            logger.warning("YOLO Layout model not found at %s. Skipping layout segmentation.", model_path)
            return NoOpLayoutSegmenter().segment(image_path)

        img = cv2.imread(image_path)
        if img is None:
            logger.error("Could not read image at %s", image_path)
            return []

        model = self._get_model()
        results = model.predict(img, conf=self._confidence)

        regions = []
        receipt_dir = Path(image_path).parent / "layout"
        receipt_dir.mkdir(exist_ok=True)

        for result in results:
            for i, box in enumerate(result.boxes):
                label_id = int(box.cls[0])
                label = result.names[label_id]
                conf = float(box.conf[0])

                x1, y1, x2, y2 = map(int, box.xyxy[0])
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(img.shape[1], x2), min(img.shape[0], y2)

                crop = img[y1:y2, x1:x2]
                if crop.size > 0:
                    crop_filename = f"{label}_{i}.png"
                    crop_path = receipt_dir / crop_filename
                    cv2.imwrite(str(crop_path), crop)

                    regions.append(LayoutRegion(
                        label=label,
                        image_path=crop_path,
                        confidence=conf,
                        bbox=[x1, y1, x2, y2]
                    ))

        if not regions:
            logger.warning("YOLO Layout detected no regions. Falling back to whole image.")
            return NoOpLayoutSegmenter().segment(image_path)

        return regions

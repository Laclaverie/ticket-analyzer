import logging
import os
import shutil
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path

logger = logging.getLogger(__name__)


class BaseOcrClient(ABC):
    @abstractmethod
    def extract_text(self, image_path: str) -> str:
        """Return extracted OCR text for the image path."""


class DonutOcrClient(BaseOcrClient):
    """
    Experimental OCR client that uses the Donut transformer model.
    """
    def __init__(self, model_path: str = "naver-clova-ix/donut-base-finetuned-rvl-cdip") -> None:
        self._model_path = model_path
        self._processor = None
        self._model = None

    def _load_model(self):
        if self._model is None:
            try:
                from transformers import DonutProcessor, VisionEncoderDecoderModel
                import torch

                device = "cuda" if torch.cuda.is_available() else "cpu"
                self._processor = DonutProcessor.from_pretrained(self._model_path)
                self._model = VisionEncoderDecoderModel.from_pretrained(self._model_path)
                self._model.to(device)
            except ImportError:
                logger.error("transformers or torch not found. Donut OCR will be unavailable.")
                raise ImportError("Please install transformers and torch to use DonutOcrClient.")

    def extract_text(self, image_path: str) -> str:
        # This is a placeholder for experimental Donut integration
        # In a real scenario, it would return structured JSON or plain text
        logger.info("Donut OCR (Experimental) requested for %s", image_path)
        return f"Donut OCR result for {image_path}"


class AutoOcrClient(BaseOcrClient):
    """
    OCR adapter that uses local tesseract when available.

    Falls back to deterministic filename-derived text so development and tests
    keep working on machines where tesseract is not installed.
    """

    def __init__(self, tesseract_cmd: str | None = None) -> None:
        self._tesseract_cmd = tesseract_cmd

    def extract_text(self, image_path: str) -> str:
        tesseract_path = self._tesseract_cmd or shutil.which("tesseract")

        # As a last resort on Windows, try common installation paths if not in PATH
        if not tesseract_path and os.name == "nt":
            common_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            ]
            for path in common_paths:
                if os.path.exists(path):
                    tesseract_path = path
                    break

        if tesseract_path:
            logger.info("Using Tesseract OCR at: %s", tesseract_path)
            try:
                result = subprocess.run(
                    [tesseract_path, image_path, "stdout"],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    check=False,
                )
                if result.returncode == 0 and result.stdout and result.stdout.strip():
                    return result.stdout
                logger.warning(
                    "Tesseract execution failed for %s (code=%s). Using fallback text.",
                    image_path,
                    result.returncode,
                )
            except Exception as e:
                logger.error("Error during Tesseract execution: %s", e)
        else:
            logger.info("Tesseract not found in PATH. Using filename fallback for OCR.")

        return self._fallback_text(image_path)

    @staticmethod
    def _fallback_text(image_path: str) -> str:
        stem = Path(image_path).stem.strip()
        logger.debug("Generating fallback text from filename stem: %s", stem)
        if not stem:
            return "unreadable receipt"
        return stem.replace("_", " ").replace("-", " ")

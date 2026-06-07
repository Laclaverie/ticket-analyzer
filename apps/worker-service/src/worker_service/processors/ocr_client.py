import logging
import shutil
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path

logger = logging.getLogger(__name__)


class BaseOcrClient(ABC):
    @abstractmethod
    def extract_text(self, image_path: str) -> str:
        """Return extracted OCR text for the image path."""


class AutoOcrClient(BaseOcrClient):
    """
    OCR adapter that uses local tesseract when available.

    Falls back to deterministic filename-derived text so development and tests
    keep working on machines where tesseract is not installed.
    """

    def extract_text(self, image_path: str) -> str:
        tesseract_path = shutil.which("tesseract")
        if tesseract_path:
            result = subprocess.run(
                [tesseract_path, image_path, "stdout"],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout
            logger.warning(
                "Tesseract execution failed for %s (code=%s). Using fallback text.",
                image_path,
                result.returncode,
            )

        return self._fallback_text(image_path)

    @staticmethod
    def _fallback_text(image_path: str) -> str:
        stem = Path(image_path).stem.strip()
        if not stem:
            return "unreadable receipt"
        return stem.replace("_", " ").replace("-", " ")

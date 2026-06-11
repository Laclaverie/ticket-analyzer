import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class BaseImagePreprocessor(ABC):
    """Abstract base class for image pre-processing steps."""
    @abstractmethod
    def process(self, image_path: str) -> str:
        """
        Processes the image at the given path and returns the path to the
        pre-processed image.
        """

class NoOpPreprocessor(BaseImagePreprocessor):
    """Default preprocessor that does nothing and returns the original path."""
    def process(self, image_path: str) -> str:
        logger.debug("No-op preprocessing: using original image path %s", image_path)
        return image_path

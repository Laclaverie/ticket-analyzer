import logging
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

import cv2
import numpy as np

logger = logging.getLogger(__name__)

class ImageStep(ABC):
    """Abstract base class for a single image processing step."""
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the processing step."""

    @abstractmethod
    def apply(self, input_path: Path, output_path: Path) -> None:
        """Apply the processing step to the image at input_path and save to output_path."""

class BaseImagePreprocessor(ABC):
    """Abstract base class for image pre-processing steps."""
    @abstractmethod
    def process(self, image_path: str, debug: bool = False) -> str:
        """
        Processes the image at the given path and returns the path to the
        pre-processed image.
        """

class NoOpPreprocessor(BaseImagePreprocessor):
    """Default preprocessor that does nothing and returns the original path."""
    def process(self, image_path: str, debug: bool = False) -> str:
        logger.debug("No-op preprocessing: using original image path %s", image_path)
        return image_path

class CopyStep(ImageStep):
    """A simple step that copies the input image to the output path."""
    @property
    def name(self) -> str:
        return "Copy"

    def apply(self, input_path: Path, output_path: Path) -> None:
        shutil.copy2(input_path, output_path)

class GrayscaleStep(ImageStep):
    """Converts the image to grayscale."""
    @property
    def name(self) -> str:
        return "Grayscale"

    def apply(self, input_path: Path, output_path: Path) -> None:
        img = cv2.imread(str(input_path))
        if img is None:
            raise ValueError(f"Could not read image at {input_path}")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(str(output_path), gray)

class ThresholdStep(ImageStep):
    """Applies adaptive thresholding to the image."""
    @property
    def name(self) -> str:
        return "Threshold"

    def apply(self, input_path: Path, output_path: Path) -> None:
        img = cv2.imread(str(input_path), cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise ValueError(f"Could not read image at {input_path}")
        # Adaptive thresholding to handle uneven lighting
        thresh = cv2.adaptiveThreshold(
            img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        cv2.imwrite(str(output_path), thresh)

class RescaleStep(ImageStep):
    """Rescales the image to a minimum width for better OCR."""
    def __init__(self, min_width: int = 2000) -> None:
        self._min_width = min_width

    @property
    def name(self) -> str:
        return f"Rescale_{self._min_width}"

    def apply(self, input_path: Path, output_path: Path) -> None:
        img = cv2.imread(str(input_path))
        if img is None:
            raise ValueError(f"Could not read image at {input_path}")

        height, width = img.shape[:2]
        if width < self._min_width:
            scaling_factor = self._min_width / width
            new_size = (self._min_width, int(height * scaling_factor))
            rescaled = cv2.resize(img, new_size, interpolation=cv2.INTER_CUBIC)
            cv2.imwrite(str(output_path), rescaled)
        else:
            shutil.copy2(input_path, output_path)

class PipelinePreprocessor(BaseImagePreprocessor):
    """Executes a series of ImageSteps, optionally saving intermediary debug images."""
    def __init__(self, steps: List[ImageStep]) -> None:
        self._steps = steps

    def process(self, image_path: str, debug: bool = False) -> str:
        if not self._steps:
            return image_path

        input_file = Path(image_path)
        receipt_dir = input_file.parent

        # We'll use the last successful output as the final result
        current_input = input_file

        debug_dir = None
        if debug:
            debug_dir = receipt_dir / "pre_steps"
            debug_dir.mkdir(parents=True, exist_ok=True)
            logger.info("Debug mode enabled. Saving intermediary steps to: %s", debug_dir)

        # To keep filenames clean and avoid overwriting in long pipelines,
        # we'll create a temporary working copy if we don't want to mess with original
        # but the request says original is at root and pre steps in a folder.

        for i, step in enumerate(self._steps, start=1):
            step_name = step.name.replace(" ", "_")
            # Intermediary filename format: {step_index}_{StepName}.png
            # Using .png as requested for intermediary steps
            output_filename = f"{i}_{step_name}.png"

            if debug:
                output_path = debug_dir / output_filename
            else:
                # In non-debug mode, we might just use a temp file or keep it in memory
                # For now, let's keep it simple and use a hidden temp file in the same dir
                output_path = receipt_dir / f".tmp_step_{i}.png"

            logger.debug("Executing step %d: %s -> %s", i, step.name, output_path)
            step.apply(current_input, output_path)
            current_input = output_path

        return str(current_input)

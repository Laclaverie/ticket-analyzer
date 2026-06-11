import logging
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

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

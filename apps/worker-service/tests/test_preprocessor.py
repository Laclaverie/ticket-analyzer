import os
from pathlib import Path
import cv2
import numpy as np
from worker_service.processors.preprocessor import (
    PipelinePreprocessor,
    ImageStep,
    CopyStep,
    GrayscaleStep,
    ThresholdStep,
    RescaleStep,
)

class MockStep(ImageStep):
    def __init__(self, name: str) -> None:
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def apply(self, input_path: Path, output_path: Path) -> None:
        # Just create an empty file to simulate processing
        output_path.write_text("processed")

def test_pipeline_preprocessor_debug_mode(tmp_path):
    # Setup: a dummy original image file
    receipt_dir = tmp_path / "receipt-123"
    receipt_dir.mkdir()
    original_path = receipt_dir / "original.jpg"
    original_path.write_text("original content")

    # Pipeline with 2 steps
    steps = [MockStep("Grayscale"), MockStep("Threshold")]
    preprocessor = PipelinePreprocessor(steps)

    # Execution with debug=True
    final_path = preprocessor.process(str(original_path), debug=True)

    # Verification: directory structure
    debug_dir = receipt_dir / "pre_steps"
    assert debug_dir.exists()
    assert debug_dir.is_dir()

    # Verification: naming convention
    step1_file = debug_dir / "1_Grayscale.png"
    step2_file = debug_dir / "2_Threshold.png"

    assert step1_file.exists()
    assert step2_file.exists()
    assert final_path == str(step2_file)

def test_pipeline_preprocessor_no_debug_mode(tmp_path):
    receipt_dir = tmp_path / "receipt-456"
    receipt_dir.mkdir()
    original_path = receipt_dir / "original.jpg"
    original_path.write_text("original content")

    steps = [MockStep("Grayscale")]
    preprocessor = PipelinePreprocessor(steps)

    # Execution with debug=False
    final_path = preprocessor.process(str(original_path), debug=False)

    # Verification: pre_steps should NOT exist
    debug_dir = receipt_dir / "pre_steps"
    assert not debug_dir.exists()

    # Final path should be the hidden temp file from the last step
    assert Path(final_path).name == ".tmp_step_1.png"
    assert Path(final_path).exists()

def test_copy_step_works(tmp_path):
    input_file = tmp_path / "input.jpg"
    input_file.write_text("image data")
    output_file = tmp_path / "output.jpg"

    step = CopyStep()
    assert step.name == "Copy"
    step.apply(input_file, output_file)

    assert output_file.exists()
    assert output_file.read_text() == "image data"

def test_advanced_steps_execution(tmp_path):
    # Create a small dummy BGR image
    input_path = tmp_path / "test.jpg"
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.imwrite(str(input_path), img)

    # Grayscale
    gray_path = tmp_path / "gray.png"
    GrayscaleStep().apply(input_path, gray_path)
    assert gray_path.exists()
    res = cv2.imread(str(gray_path))
    assert len(res.shape) == 2 or res.shape[2] == 1 or np.all(res[:,:,0] == res[:,:,1])

    # Threshold (on grayscale)
    thresh_path = tmp_path / "thresh.png"
    ThresholdStep().apply(gray_path, thresh_path)
    assert thresh_path.exists()

    # Rescale
    rescale_path = tmp_path / "rescale.png"
    RescaleStep(min_width=200).apply(input_path, rescale_path)
    assert rescale_path.exists()
    rescaled_img = cv2.imread(str(rescale_path))
    assert rescaled_img.shape[1] == 200

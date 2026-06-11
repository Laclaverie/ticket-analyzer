import os
from pathlib import Path
from worker_service.processors.preprocessor import PipelinePreprocessor, ImageStep, CopyStep

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

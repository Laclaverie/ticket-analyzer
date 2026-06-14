import pytest
import numpy as np
import cv2
from pathlib import Path
from unittest.mock import MagicMock, patch
from worker_service.processors.preprocessor import YoloDetectionStep

@pytest.fixture
def mock_image(tmp_path):
    img_path = tmp_path / "test_receipt.jpg"
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.imwrite(str(img_path), img)
    return img_path

def test_yolo_step_no_model(mock_image, tmp_path):
    output_path = tmp_path / "output.jpg"
    step = YoloDetectionStep(model_path="non_existent.pt")
    step.apply(mock_image, output_path)
    assert output_path.exists()
    # Should just copy
    assert output_path.stat().st_size > 0

@patch("worker_service.processors.preprocessor.YoloDetectionStep._get_model")
def test_yolo_step_single_detection(mock_get_model, mock_image, tmp_path):
    output_path = tmp_path / "output.jpg"
    step = YoloDetectionStep(model_path="dummy.pt")

    # Mock YOLO result
    mock_model = MagicMock()
    mock_get_model.return_value = mock_model

    mock_box = MagicMock()
    mock_box.xyxy = [np.array([10, 10, 50, 50])]

    mock_result = MagicMock()
    mock_result.boxes = [mock_box]
    mock_model.predict.return_value = [mock_result]

    with patch("worker_service.processors.preprocessor.Path.exists", return_value=True):
        step.apply(mock_image, output_path)

    assert output_path.exists()
    img = cv2.imread(str(output_path))
    assert img.shape == (40, 40, 3)

@patch("worker_service.processors.preprocessor.YoloDetectionStep._get_model")
def test_yolo_step_multiple_detections(mock_get_model, mock_image, tmp_path):
    output_path = tmp_path / "output.jpg"
    step = YoloDetectionStep(model_path="dummy.pt")

    # Mock YOLO result with 2 boxes
    mock_model = MagicMock()
    mock_get_model.return_value = mock_model

    box1 = MagicMock()
    box1.xyxy = [np.array([0, 0, 10, 10])]
    box2 = MagicMock()
    box2.xyxy = [np.array([20, 20, 40, 40])]

    mock_result = MagicMock()
    mock_result.boxes = [box1, box2]
    mock_model.predict.return_value = [mock_result]

    with patch("worker_service.processors.preprocessor.Path.exists", return_value=True):
        step.apply(mock_image, output_path)

    assert output_path.exists()
    img = cv2.imread(str(output_path))
    # Box 1 is 10x10, Box 2 is 20x20.
    # Max width is 20. Stacking 10+20 = 30 height.
    assert img.shape == (30, 20, 3)

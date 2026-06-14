# YOLO Segmentation for Receipt Extraction

This project supports using a YOLOv8-seg model to improve receipt detection by isolating the ticket from the background.

## How to use

1.  **Dependencies:**
    The `ultralytics` library is included in `pyproject.toml` as a standard dependency.

2.  **Model Weights:**
    Place your trained YOLO weights (e.g., `best.pt`) in the project. The default path is `apps/worker-service/data/weights/best.pt`.

3.  **Configuration:**
    Update your `.env` file or environment variables:
    ```env
    YOLO_ENABLED=True
    USE_YOLO_PIPELINE=True
    YOLO_MODEL_PATH=apps/worker-service/data/weights/best.pt
    YOLO_CONFIDENCE=0.55
    ```

    - `YOLO_ENABLED`: Master switch for YOLO features.
    - `USE_YOLO_PIPELINE`:
      - `True` (default): Uses YOLO detection as the *exclusive* segmentation step.
      - `False`: Uses YOLO detection followed by legacy preprocessing (Grayscale, Threshold, Rescale).

## Features

- **Automatic Cropping:** Only the detected receipt is passed to the OCR engine.
- **Multi-Ticket Support:** If multiple receipts are detected in a single photo, they are automatically cropped and stacked vertically into a single image for processing.
- **Improved OCR:** By removing background noise, Tesseract's accuracy is significantly increased.

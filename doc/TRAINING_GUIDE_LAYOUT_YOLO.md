# Training Guide: YOLO Layout & Line Detection

This guide helps you prepare a dataset to train a YOLOv8 model for segmenting supermarket receipts into regions and detecting individual lines.

## 1. Class Definitions

To use the new `YoloLayoutSegmenter` architecture, your model should ideally detect these 4 classes:

1.  **header**: The top part of the receipt (Store name, logo, address, phone).
2.  **body**: The main list containing items and prices.
3.  **footer**: The bottom part (Subtotal, Tax, Total, payment info).
4.  **line_item** (Optional but recommended): Each individual row in the body.

## 2. Labeling Tools

We recommend using one of the following:
*   **CVAT:** Robust, web-based, supports interpolation.
*   **LabelImg / Label Studio:** Simple, local, saves directly in YOLO format.
*   **Roboflow:** Very user-friendly, handles augmentation and export automatically.

## 3. Labeling Strategy

### Layout (Header/Body/Footer)
*   Draw one large box for the **header**, one for the **body**, and one for the **footer**.
*   Ensure the boxes cover the full width of the receipt.
*   Avoid overlapping the boxes if possible.

### Line-Item (The "Robust" Mode)
*   Draw a tight bounding box around **each individual line** in the body.
*   If a line is crunched but human-readable, still box it.
*   This is the most time-consuming part but yields the best results for damaged tickets.

## 4. Dataset Organization

Organize your files as follows:
```
data/
  train/
    images/ (receipt_01.jpg, ...)
    labels/ (receipt_01.txt, ...)
  val/
    images/
    labels/
  dataset.yaml
```

**dataset.yaml:**
```yaml
path: ./data
train: train/images
val: val/images
names:
  0: header
  1: body
  2: footer
  3: line_item
```

## 5. Training (on your RTX 3050)

Run the following in your terminal:

```bash
yolo task=detect mode=train model=yolov8n.pt data=dataset.yaml epochs=100 imgsz=640 device=0
```

*   **imgsz=640**: Good for layout. If you detect small lines, consider `imgsz=1024`.
*   **model=yolov8n.pt**: Start with 'Nano' (smallest) to stay within 4GB VRAM.

## 6. Deployment

Once trained, copy your `best.pt` to:
`apps/worker-service/data/weights/layout_best.pt`

And enable it in your `.env`:
```env
LAYOUT_SEGMENTATION_ENABLED=True
YOLO_LAYOUT_MODEL_PATH=apps/worker-service/data/weights/layout_best.pt
```

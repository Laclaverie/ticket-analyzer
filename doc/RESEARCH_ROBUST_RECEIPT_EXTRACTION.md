# Research: Robust Receipt Extraction Strategy

This document explores the evolution of the receipt processing pipeline from a Tesseract-based approach to a more robust, layout-aware system capable of handling "crunched" or damaged tickets.

## 1. Current Pipeline & Limitations

**Current Stack:** YOLOv8 (Segmentation) -> Tesseract (OCR) -> Regex (Parsing).

**Identified Issues:**
*   **Line Mixing:** Tesseract sometimes merges text from adjacent lines, especially if the receipt is crunched, causing regex parsers to fail.
*   **Noise Sensitivity:** Random characters are often detected in shadows or crinkles.
*   **Rigid Parsing:** Store detection and item extraction rely on global text flow, which is easily disrupted by missing letters.

## 2. Proposed Architecture: Layout-Aware "Detect-then-OCR"

The goal is to move away from treating the receipt as a single block of text and instead treat it as a structured document with distinct regions.

### Phase 1: Layout Segmentation (YOLO Layout)
Instead of just detecting the "receipt" boundary, a second YOLO model will be trained to identify:
*   **Header:** Store name, address, phone.
*   **Body:** The list of items, quantities, and prices.
*   **Footer:** Subtotal, taxes, total, payment info.

**Benefits:**
- Limits the search area for store detection (only look in Header).
- Isolates the main data (Body) from noise in the Header/Footer.

### Phase 2: Line Detection & Isolate OCR
To solve "mixed lines," we can detect each individual line of text as a bounding box.
1.  Detect "Body" region.
2.  Run a "Line Detector" (YOLO or CRAFT) within the Body.
3.  Crop each line and pass it individually to the OCR engine.
4.  **Result:** Guarantees that OCR results for Line N never mix with Line N+1.

### Phase 3: Modern Model Exploration

#### A. Donut (Document Understanding Transformer)
Donut is an end-to-end model that takes an image and produces JSON directly.
*   **Pros:** No OCR or Regex needed; extremely robust to layout distortions and missing characters.
*   **Cons:** Higher VRAM usage; slower inference; requires specific training for supermarket receipts.

#### B. PaddleOCR
A high-performance OCR suite that includes excellent text detection and recognition.
*   **Pros:** Significantly more accurate than Tesseract for "natural scene" photos; handles rotation and distortion better.

## 3. Implementation Roadmap

1.  **Modular Interfaces:** Define `BaseLayoutSegmenter` and `BaseOcrClient` to allow swapping Tesseract for PaddleOCR or Donut.
2.  **YOLO Layout Training:** User-led effort to label ~200-500 receipts with Header/Body/Footer boxes.
3.  **Region-Based Processing:** Update `OcrProcessor` to handle crops instead of full-page text.

## 4. Hardware Optimization (RTX 3050 / 4GB VRAM)

*   **Model Quantization:** Use FP16 or INT8 quantization for YOLO and OCR models to stay within 4GB VRAM.
*   **Batching:** Process lines in small batches or sequentially to avoid OOM (Out of Memory) errors.
*   **Inference Engine:** Use `ONNX Runtime` or `TensorRT` for faster execution on NVIDIA hardware.

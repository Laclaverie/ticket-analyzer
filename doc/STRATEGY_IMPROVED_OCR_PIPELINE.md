# Strategy: Improved OCR Pipeline for Supermarket Tickets

This document outlines a roadmap to evolve the current "regex-only" OCR pipeline into a robust, high-precision extraction system, specifically optimized for stores like Costco and IGA.

## 1. Image Pre-processing (The Foundation)

Currently, the system passes raw uploads directly to Tesseract. For real-world photos (shadows, perspective, crumples), the following steps are recommended:

*   **Perspective Correction (Deskewing):** Use contour detection (OpenCV) to find the receipt edges and apply a four-point perspective transform. This transforms a slanted "photo" into a flat "scan."
*   **Adaptive Thresholding:** Convert the image to grayscale and apply Gaussian or Otsu thresholding. This eliminates shadows and highlights, making text "pop" against a clean white background.
*   **Denoising:** Apply bilateral filters to remove sensor noise while preserving the sharp edges of text characters.
*   **Rescaling:** Tesseract performs best when characters are ~30 pixels high. Downscaling or upscaling to a standard width (e.g., 2000px) improves consistency.

## 2. Layout Analysis (Segmentation)

Instead of treating the receipt as a single block of text, the pipeline should segment it into three functional zones:

1.  **Header:** Contains Store Name, Address, Date, and Time.
    *   *Strategy:* Use high-confidence anchor words (e.g., "MEMBER", "ST#") to find the top.
2.  **Body (Items):** The main list of SKUs, names, and prices.
    *   *Strategy:* Use the detected "Body" area to isolate line items. Identify the "Price Column" via vertical alignment (X-coordinates) to prevent SKU numbers from being confused with prices.
3.  **Footer:** Contains Subtotal, Tax, and Total.
    *   *Strategy:* Scan from the bottom up for keywords like "TOTAL", "AMOUNT DUE".

## 3. Costco-Specific Enhancements

Based on the `original.jpg` sample, several Costco-specific patterns can be optimized:

*   **TPD (Temporary Price Discount) Linking:**
    *   *Pattern:* Lines starting with `TPD/` or ending with `-` immediately following an item.
    *   *Logic:* If a line matches the `TPD` pattern, it should be merged as a discount to the *previous* item rather than treated as a standalone item.
*   **SKU Validation:** Costco SKUs are typically 5-7 digits. Using this as a strong signal for the start of a "Line Item" reduces noise from the header/footer.
*   **Tax Code Filtering:** Letters like `H`, `P`, `E`, `F` at the end of the line are tax indicators. These should be stripped during name normalization but used to verify the `TAX` row in the footer.
*   **Total Verification (Check Sum):**
    *   *Logic:* `SUM(items.line_total) == SUB_TOTAL`. `SUB_TOTAL + TAX == TOTAL`.
    *   If the math doesn't add up, the system should flag the receipt for manual review or attempt a "re-scan" with different thresholding parameters.

## 4. Proposed Architectural Skeleton

To support this without bloating the `OcrProcessor`, we introduce an `ImagePreprocessor` chain:

```python
class BaseImagePreprocessor(ABC):
    @abstractmethod
    def process(self, image_path: str) -> str:
        """Returns path to the enhanced image."""

class ScanEnhancer(BaseImagePreprocessor):
    """Applies Grayscale -> Threshold -> Deskew."""
    ...

class OcrProcessor:
    def process(self, job_id: str):
        # 1. Enhance
        enhanced_image = self.preprocessor.process(raw_image)
        # 2. Extract
        text = self.ocr_client.extract_text(enhanced_image)
        # 3. Parse (with layout context)
        ...
```

## 5. Next Steps (Implementation Phases)

1.  **Phase A (Architecture):** Integrate the `BaseImagePreprocessor` skeleton into the worker.
2.  **Phase B (Vision - Optional Dependency):** Implement a `VisionPreprocessor` using `OpenCV` and `numpy`. These should be optional dependencies (e.g., `pip install .[vision]`).
3.  **Phase C (Parsing):** Update `CostcoParser` to handle `TPD/` line linking.

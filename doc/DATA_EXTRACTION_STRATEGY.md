# Data Extraction Strategy: From OCR to Structured Insights

This document outlines the strategy for extracting structured data from supermarket tickets using local, open-source tools. It covers the current implementation, store-specific optimizations, and the roadmap toward a robust AI-driven pipeline.

---

## 1. Current Architecture (V0)

The system currently employs a "Pipe and Filter" architecture for receipt processing:

1.  **OCR Layer (`AutoOcrClient`)**: Uses **Tesseract OCR** locally to produce raw text. It treats the receipt as a single stream of characters, often losing layout information.
2.  **Parsing Layer (`parsing-core`)**: Uses **Regex-based heuristics** to find lines that look like items (e.g., `Name Quantity x Price`).
3.  **Classification Layer (`taxonomy-core`)**: Uses **Keyword matching** to assign categories based on the product name.

### Limitations:
- Sensitive to OCR "noise" (misread characters).
- Brittle when encountering new receipt layouts.
- Limited context (doesn't know which store it is unless explicitly parsed).

---

## 2. Strategy: Template-Based Parsing (Short-term)

For high-volume stores like **Costco** or **IGA**, a generic regex is often insufficient due to unique formatting (e.g., Costco's multi-column layout or IGA's specific tax codes).

### The "Store-First" Logic:
1.  **Identify**: Check the first 5–10 lines for known store names or patterns.
2.  **Dispatch**: Use a specialized parser class (`CostcoParser`, `IgaParser`) that inherits from a base `ReceiptParser`.
3.  **Extract**: Use store-specific regex that accounts for:
    - Date/Time locations.
    - Tax indicators (A, B, H).
    - Member IDs or discount rows.

**Pros**: Extremely high accuracy for supported stores.
**Cons**: Maintenance overhead for every new supermarket added.

---

## 3. Strategy: Local AI & Machine Learning (Mid-term)

To move beyond fragile regex, we should leverage local Machine Learning models that understand **Document Layout**.

### A. Local LLMs (Large Language Models)
Instead of regex, we can feed the raw OCR text into a small, local LLM (e.g., **Llama 3 8B** or **Mistral** via Ollama) with a structured prompt:
> "Extract the items, quantities, and prices from this receipt text into JSON format."

### B. Specialized Layout Models (LayoutLM / Donut)
- **LayoutLM**: Understands both the text and its 2D position (bounding boxes) on the page.
- **Donut (OCR-free Transformer)**: Can read the image directly and output structured JSON without a separate OCR step.
- **Benefit**: These models can be run locally using libraries like `transformers` or `onnxruntime`.

### C. Manual Annotation & Training
To achieve professional-grade results, we should start building a **Local Dataset**:
1.  **Tooling**: Integrate a simple labeling UI in the Debug page where users can "correct" the parser.
2.  **Fine-tuning**: Use these corrections to fine-tune a model like LayoutLM specifically on *your* common supermarket tickets.
3.  **Synthetic Data**: Generate "fake" receipts with known data to bootstrap training.

---

## 4. Deep Classification Strategy

The user requirement is to distinguish between food (fresh, processed, meat) and non-food (home, pharmacy).

### Multi-Level Taxonomy:
- **Level 1 (Sector)**: Food, Health, Home, Clothing.
- **Level 2 (Category)**: (Food -> Meat), (Health -> Pharmacy).
- **Level 3 (Type)**: (Meat -> Beef), (Fresh -> Organic).

### Technical Approach:
- **Embeddings**: Convert product names (e.g., "ORGANIC CHICKEN BRST") into vectors using a local embedding model (e.g., `sentence-transformers`).
- **Vector Search**: Compare the product vector against a pre-labeled database of common items. This is far more robust than keyword matching (e.g., it knows "Poulet" and "Chicken" are similar).

---

## 5. Roadmap

### Phase 1: The Heuristic Foundation (Current - Next 1 Month)
- Improve `parsing-core` with Store-Detection.
- Implement dedicated parsers for Costco and IGA.
- Extract "Total", "Tax", and "Store Name" explicitly.

### Phase 2: Human-in-the-Loop (Next 3 Months)
- Add "Correction" UI to the Web Client.
- Save "Corrected" JSONs to a local `training_data/` folder.
- Implement a basic local LLM fallback for unrecognized formats.

### Phase 3: The Neural Shift (Next 6 Months+)
- Transition to a Layout-Aware model (LayoutLM) for primary extraction.
- Deploy local vector embeddings for advanced classification.
- **Android Integration**: Move the initial OCR step to the phone (Google ML Kit) to send structured text + bounding boxes to the backend, reducing backend CPU load.

---

## 6. Implementation Principles
- **Privacy First**: All processing stays on-premise. No data leaves the server.
- **Transparency**: The UI should always show *how* a piece of data was derived (Regex vs AI vs Manual).
- **Incrementalism**: The system should work with a simple regex and get *better* as more AI components are "plugged in".

from typing import List
from .stores import StoreType

class StoreDetector:
    """Detects the store from receipt text."""

    def detect(self, lines: List[str]) -> StoreType:
        # Check first 10 lines for store name
        header = " ".join(lines[:10]).lower()

        if "costco" in header:
            return StoreType.COSTCO
        if "iga" in header or "viva" in header: # Some IGA receipts might have specific banners
            return StoreType.IGA

        return StoreType.UNKNOWN

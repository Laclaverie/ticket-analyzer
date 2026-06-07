from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Category:
    id: str
    name: str
    slug: str
    parent_id: Optional[str]
    is_food: bool

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("Category id cannot be empty")
        if not self.name:
            raise ValueError("Category name cannot be empty")
        if not self.slug:
            raise ValueError("Category slug cannot be empty")

from __future__ import annotations

from typing import Optional

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from persistence.base import Base


class CategoryORM(Base):
    __tablename__ = "categories"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    slug: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    parent_id: Mapped[Optional[str]] = mapped_column(
        String, ForeignKey("categories.id"), nullable=True
    )
    is_food: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    children: Mapped[list[CategoryORM]] = relationship("CategoryORM", back_populates="parent")
    parent: Mapped[Optional[CategoryORM]] = relationship(
        "CategoryORM", back_populates="children", remote_side=[id]
    )

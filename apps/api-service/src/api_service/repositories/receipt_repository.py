import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from domain_models.receipt import Receipt, ReceiptImage
from persistence.models.receipt import ReceiptORM, ReceiptImageORM
from persistence.models.receipt_item import ReceiptItemNormalizedORM, ReceiptItemRawORM


class ReceiptRepository:
    """
    Translates between ReceiptORM/ReceiptImageORM and domain objects.
    All SQL is isolated here — callers never see ORM types.
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    def save(self, store: Optional[str], currency: str) -> Receipt:
        orm = ReceiptORM(
            id=str(uuid.uuid4()),
            store=store,
            currency=currency,
            created_at=datetime.now(timezone.utc),
        )
        self._db.add(orm)
        self._db.flush()
        return self._to_domain(orm)

    def save_image(self, receipt_id: str, file_path: str, file_hash: str) -> ReceiptImage:
        orm = ReceiptImageORM(
            id=str(uuid.uuid4()),
            receipt_id=receipt_id,
            file_path=file_path,
            file_hash=file_hash,
            created_at=datetime.now(timezone.utc),
        )
        self._db.add(orm)
        self._db.flush()
        return self._image_to_domain(orm)

    def find_by_id(self, receipt_id: str) -> Optional[Receipt]:
        orm = self._db.get(ReceiptORM, receipt_id)
        return self._to_domain(orm) if orm else None

    def find_detail_orm(self, receipt_id: str) -> Optional[ReceiptORM]:
        """Return the raw ORM with images eagerly available for detail views."""
        return self._db.get(ReceiptORM, receipt_id)

    def list_all(self, offset: int, limit: int) -> tuple[list[ReceiptORM], int]:
        """Return (page of ORM rows, total count)."""
        total: int = self._db.query(ReceiptORM).count()
        rows = (
            self._db.query(ReceiptORM)
            .order_by(ReceiptORM.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return rows, total

    def find_normalized_items(self, receipt_id: str) -> list[ReceiptItemNormalizedORM]:
        """Return all normalized items for a receipt ordered by line number."""
        return (
            self._db.query(ReceiptItemNormalizedORM)
            .join(ReceiptItemRawORM, ReceiptItemNormalizedORM.receipt_item_raw_id == ReceiptItemRawORM.id)
            .filter(ReceiptItemRawORM.receipt_id == receipt_id)
            .order_by(ReceiptItemRawORM.line_number)
            .all()
        )

    @staticmethod
    def _to_domain(orm: ReceiptORM) -> Receipt:
        return Receipt(
            id=orm.id,
            store=orm.store,
            purchase_date=orm.purchase_date,
            total_amount=orm.total_amount,
            currency=orm.currency,
            created_at=orm.created_at,
        )

    @staticmethod
    def _image_to_domain(orm: ReceiptImageORM) -> ReceiptImage:
        return ReceiptImage(
            id=orm.id,
            receipt_id=orm.receipt_id,
            file_path=orm.file_path,
            file_hash=orm.file_hash,
            created_at=orm.created_at,
        )

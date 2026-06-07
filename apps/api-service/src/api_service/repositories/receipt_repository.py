import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from domain_models.receipt import Receipt, ReceiptImage
from persistence.models.receipt import ReceiptORM, ReceiptImageORM


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

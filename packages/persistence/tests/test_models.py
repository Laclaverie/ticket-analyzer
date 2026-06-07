from persistence.models.receipt import ReceiptORM, ReceiptImageORM
from persistence.models.category import CategoryORM
from persistence.models.processing_job import ProcessingJobORM
from persistence.models.receipt_item import ReceiptItemRawORM


def test_can_create_and_retrieve_receipt(db_session):
    receipt = ReceiptORM(currency="EUR")
    db_session.add(receipt)
    db_session.commit()

    result = db_session.get(ReceiptORM, receipt.id)
    assert result is not None
    assert result.currency == "EUR"


def test_receipt_auto_generates_id(db_session):
    r1 = ReceiptORM(currency="EUR")
    r2 = ReceiptORM(currency="CAD")
    db_session.add_all([r1, r2])
    db_session.commit()

    assert r1.id != r2.id
    assert r1.id is not None


def test_receipt_image_links_to_receipt(db_session):
    receipt = ReceiptORM(currency="EUR")
    db_session.add(receipt)
    db_session.flush()

    image = ReceiptImageORM(
        receipt_id=receipt.id,
        file_path="/data/test.jpg",
        file_hash="sha256abc",
    )
    db_session.add(image)
    db_session.commit()

    loaded = db_session.get(ReceiptORM, receipt.id)
    assert len(loaded.images) == 1
    assert loaded.images[0].file_hash == "sha256abc"


def test_processing_job_default_status_is_pending(db_session):
    receipt = ReceiptORM(currency="EUR")
    db_session.add(receipt)
    db_session.flush()

    job = ProcessingJobORM(receipt_id=receipt.id)
    db_session.add(job)
    db_session.commit()

    loaded = db_session.get(ProcessingJobORM, job.id)
    assert loaded.status == "pending"
    assert loaded.error_message is None


def test_processing_job_auto_generates_id(db_session):
    receipt = ReceiptORM(currency="EUR")
    db_session.add(receipt)
    db_session.flush()

    j1 = ProcessingJobORM(receipt_id=receipt.id)
    j2 = ProcessingJobORM(receipt_id=receipt.id)
    db_session.add_all([j1, j2])
    db_session.commit()

    assert j1.id != j2.id


def test_category_self_referential_hierarchy(db_session):
    parent = CategoryORM(id="food", name="Food", slug="food", is_food=True)
    child = CategoryORM(
        id="food-dairy", name="Dairy", slug="food-dairy", parent_id="food", is_food=True
    )
    db_session.add_all([parent, child])
    db_session.commit()

    loaded = db_session.get(CategoryORM, "food-dairy")
    assert loaded.parent_id == "food"


def test_receipt_item_raw_links_to_receipt(db_session):
    receipt = ReceiptORM(currency="EUR")
    db_session.add(receipt)
    db_session.flush()

    item = ReceiptItemRawORM(receipt_id=receipt.id, raw_text="LAIT 1L 1.29", line_number=3)
    db_session.add(item)
    db_session.commit()

    loaded = db_session.get(ReceiptItemRawORM, item.id)
    assert loaded.raw_text == "LAIT 1L 1.29"
    assert loaded.line_number == 3


def test_processing_job_status_can_be_updated(db_session):
    receipt = ReceiptORM(currency="EUR")
    db_session.add(receipt)
    db_session.flush()

    job = ProcessingJobORM(receipt_id=receipt.id)
    db_session.add(job)
    db_session.commit()

    job.status = "completed"
    db_session.commit()

    loaded = db_session.get(ProcessingJobORM, job.id)
    assert loaded.status == "completed"

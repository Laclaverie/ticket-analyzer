from domain_models.enums import ClassificationOrigin, ConsumptionContext, ProcessingStatus


def test_processing_status_string_values():
    assert ProcessingStatus.PENDING == "pending"
    assert ProcessingStatus.IN_PROGRESS == "in_progress"
    assert ProcessingStatus.COMPLETED == "completed"
    assert ProcessingStatus.FAILED == "failed"


def test_classification_origin_string_values():
    assert ClassificationOrigin.RULE == "rule"
    assert ClassificationOrigin.MODEL == "model"
    assert ClassificationOrigin.MANUAL == "manual"


def test_consumption_context_string_values():
    assert ConsumptionContext.PERSONAL == "personal"
    assert ConsumptionContext.SHARED == "shared"
    assert ConsumptionContext.FOR_OTHERS == "for_others"


def test_processing_status_from_string():
    assert ProcessingStatus("pending") == ProcessingStatus.PENDING
    assert ProcessingStatus("completed") == ProcessingStatus.COMPLETED


def test_all_processing_statuses_are_strings():
    for status in ProcessingStatus:
        assert isinstance(status.value, str)

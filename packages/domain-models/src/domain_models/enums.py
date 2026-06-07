from enum import Enum


class ProcessingStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class ClassificationOrigin(str, Enum):
    RULE = "rule"
    MODEL = "model"
    MANUAL = "manual"


class ConsumptionContext(str, Enum):
    PERSONAL = "personal"
    SHARED = "shared"
    FOR_OTHERS = "for_others"

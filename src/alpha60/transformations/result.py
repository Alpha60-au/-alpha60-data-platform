"""Transformation result models."""

from dataclasses import dataclass
from enum import StrEnum


class TransformationStatus(StrEnum):
    """Possible transformation execution statuses."""

    SUCCESS = "success"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class TransformationResult:
    """Result from running a warehouse transformation."""

    target_table_id: str
    status: TransformationStatus
    rows_written: int | None = None
    error_message: str | None = None

"""Shared warehouse types."""

from dataclasses import dataclass
from enum import StrEnum


class WarehouseLoadStatus(StrEnum):
    """Result status for a warehouse load operation."""

    SUCCESS = "success"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class WarehouseLoadResult:
    """Result of loading records into a warehouse."""

    table_id: str
    status: WarehouseLoadStatus
    rows_loaded: int
    error_message: str | None = None
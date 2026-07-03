"""Generic warehouse loader interface."""

from collections.abc import Iterable
from typing import Protocol

from alpha60.core.models.record import Record
from alpha60.warehouse.types import WarehouseLoadResult


class WarehouseLoader(Protocol):
    """Interface for loading records into a warehouse."""

    def load(self, table_id: str, records: Iterable[Record]) -> WarehouseLoadResult:
        """Load records into the specified warehouse table."""
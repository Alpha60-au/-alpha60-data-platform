"""BigQuery warehouse loader."""

from collections.abc import Iterable

from alpha60.core.models.record import Record
from alpha60.warehouse.bigquery.config import BigQueryConfig
from alpha60.warehouse.loader import WarehouseLoader
from alpha60.warehouse.types import WarehouseLoadResult


class BigQueryLoader(WarehouseLoader):
    """Loads records into Google BigQuery."""

    def __init__(self, config: BigQueryConfig) -> None:
        """Create a new BigQuery loader."""
        self._config = config

    def load(self, table_id: str, records: Iterable[Record]) -> WarehouseLoadResult:
        """Load records into a BigQuery table."""
        raise NotImplementedError("BigQuery loading is not implemented yet.")
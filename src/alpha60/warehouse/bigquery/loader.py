"""BigQuery warehouse loader."""

from collections.abc import Iterable

from alpha60.core.models.record import Record
from alpha60.warehouse.bigquery.client import BigQueryClient
from alpha60.warehouse.bigquery.config import BigQueryConfig
from alpha60.warehouse.bigquery.rows import record_to_bigquery_row
from alpha60.warehouse.loader import WarehouseLoader
from alpha60.warehouse.types import WarehouseLoadResult, WarehouseLoadStatus


class BigQueryLoader(WarehouseLoader):
    """Loads records into Google BigQuery."""

    def __init__(
        self,
        config: BigQueryConfig,
        client: BigQueryClient,
    ) -> None:
        """Create a new BigQuery loader."""
        self._config = config
        self._client = client

    def load(
        self,
        table_id: str,
        records: Iterable[Record],
    ) -> WarehouseLoadResult:
        """Load records into a BigQuery table."""
        qualified_table_id = self._qualified_table_id(table_id)
        rows = [record_to_bigquery_row(record) for record in records]

        try:
            rows_loaded = self._client.load_rows(
                table_id=qualified_table_id,
                rows=rows,
            )
        except Exception as exc:
            return WarehouseLoadResult(
                table_id=qualified_table_id,
                status=WarehouseLoadStatus.FAILED,
                rows_loaded=0,
                error_message=str(exc),
            )

        return WarehouseLoadResult(
            table_id=qualified_table_id,
            status=WarehouseLoadStatus.SUCCESS,
            rows_loaded=rows_loaded,
        )

    def _qualified_table_id(self, table_id: str) -> str:
        """Return the fully qualified BigQuery table identifier."""
        return f"{self._config.project_id}.{self._config.dataset_id}.{table_id}"
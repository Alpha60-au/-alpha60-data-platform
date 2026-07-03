"""Google BigQuery client adapter."""

from collections.abc import Iterable
from typing import Any

from google.cloud import bigquery

from alpha60.warehouse.bigquery.config import BigQueryConfig


class GoogleBigQueryClient:
    """Google Cloud BigQuery client adapter."""

    def __init__(
        self,
        config: BigQueryConfig,
        client: bigquery.Client | None = None,
    ) -> None:
        """Create a Google BigQuery client adapter."""
        self._config = config
        self._client = client or bigquery.Client(
            project=config.project_id,
            location=config.location,
        )

    def load_rows(
        self,
        table_id: str,
        rows: Iterable[dict[str, Any]],
    ) -> int:
        """Load rows into BigQuery."""
        raise NotImplementedError("Load jobs are not implemented yet.")
"""Google BigQuery client adapter."""

from collections.abc import Iterable, Sequence
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

    def test_connection(self) -> bool:
        """Verify BigQuery dataset access."""
        dataset_ref = f"{self._config.project_id}.{self._config.dataset_id}"

        try:
            self._client.get_dataset(dataset_ref)
        except Exception:
            return False

        return True

    def load_rows(
        self,
        table_id: str,
        rows: Iterable[dict[str, Any]],
    ) -> int:
        """Load rows into BigQuery using a load job."""
        rows_to_load = list(rows)

        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        )
        load_job = self._client.load_table_from_json(
            rows_to_load,
            destination=table_id,
            job_config=job_config,
        )
        load_job.result()

        if load_job.errors:
            raise RuntimeError(f"BigQuery load failed: {load_job.errors}")

        return int(load_job.output_rows or len(rows_to_load))

    def query(
        self,
        sql: str,
        parameters: Sequence[Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Run a SQL query and return rows as dictionaries."""
        job_config = bigquery.QueryJobConfig(
            query_parameters=list(parameters or []),
        )

        query_job = self._client.query(
            sql,
            job_config=job_config,
            location=self._config.location,
        )

        return [dict(row.items()) for row in query_job.result()]
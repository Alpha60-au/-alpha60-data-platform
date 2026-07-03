"""BigQuery-backed incremental state repository."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from google.cloud import bigquery

from alpha60.state import IncrementalState
from alpha60.warehouse.bigquery.client import BigQueryClient


@dataclass(frozen=True, slots=True)
class BigQueryStateRepository:
    """Repository for reading and writing incremental state in BigQuery."""

    table_id: str
    client: BigQueryClient

    def get_state(self, job_name: str) -> IncrementalState | None:
        """Return the latest incremental state for a job."""
        rows = self.client.query(
            f"""
            SELECT
                job_name,
                cursor_field,
                cursor_value
            FROM `{self.table_id}`
            WHERE job_name = @job_name
            LIMIT 1
            """,
            parameters=[
                bigquery.ScalarQueryParameter(
                    "job_name",
                    "STRING",
                    job_name,
                ),
            ],
        )

        if not rows:
            return None

        row = rows[0]
        cursor_value = row["cursor_value"]

        if cursor_value is not None and not isinstance(cursor_value, datetime):
            raise TypeError("cursor_value must be a datetime or None")

        return IncrementalState(
            job_name=str(row["job_name"]),
            cursor_field=str(row["cursor_field"]),
            cursor_value=cursor_value,
        )

    def save_state(self, state: IncrementalState) -> None:
        """Persist incremental state for a job."""
        raise NotImplementedError
"""Shopify order staging transformation."""

from pathlib import Path
from typing import Protocol

from alpha60.transformations.result import TransformationResult, TransformationStatus
from alpha60.warehouse.bigquery.config import BigQueryConfig


_SQL_PATH = Path(__file__).parent / "sql" / "shopify" / "stg_shopify_orders.sql"


class QueryClient(Protocol):
    """Client capable of running SQL queries."""

    def query(self, sql: str) -> list[dict[str, object]]:
        """Run a SQL query and return rows as dictionaries."""


class ShopifyOrdersStagingTransformation:
    """Build the stg.shopify_orders table from raw Shopify orders."""

    def __init__(
        self,
        client: QueryClient,
        project_id: str,
        raw_dataset_id: str,
        staging_dataset_id: str,
    ) -> None:
        """Create a Shopify orders staging transformation."""
        self._client = client
        self._project_id = project_id
        self._raw_dataset_id = raw_dataset_id
        self._staging_dataset_id = staging_dataset_id

    @classmethod
    def from_config(
        cls,
        client: QueryClient,
        raw_config: BigQueryConfig,
        staging_dataset_id: str,
    ) -> "ShopifyOrdersStagingTransformation":
        """Create the transformation from BigQuery runtime config."""
        return cls(
            client=client,
            project_id=raw_config.project_id,
            raw_dataset_id=raw_config.dataset_id,
            staging_dataset_id=staging_dataset_id,
        )

    def run(self) -> TransformationResult:
        """Run the staging transformation."""
        target_table_id = (
            f"{self._project_id}.{self._staging_dataset_id}.shopify_orders"
        )

        try:
            self._client.query(self._render_sql())
        except Exception as exc:
            return TransformationResult(
                target_table_id=target_table_id,
                status=TransformationStatus.FAILED,
                error_message=str(exc),
            )

        return TransformationResult(
            target_table_id=target_table_id,
            status=TransformationStatus.SUCCESS,
        )

    def _render_sql(self) -> str:
        """Render the staging SQL with fully qualified table names."""
        template = _SQL_PATH.read_text(encoding="utf-8")

        return template.format(
            project_id=self._project_id,
            raw_dataset_id=self._raw_dataset_id,
            staging_dataset_id=self._staging_dataset_id,
        )

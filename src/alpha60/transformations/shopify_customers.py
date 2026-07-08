"""Shopify customers staging transformation factory."""

from pathlib import Path

from alpha60.transformations.runner import QueryClient, SqlTransformationRunner
from alpha60.warehouse.bigquery.config import BigQueryConfig


_SQL_PATH = Path(__file__).parent / "sql" / "shopify" / "stg_shopify_customers.sql"


def create_shopify_customers_staging_transformation(
    client: QueryClient,
    raw_config: BigQueryConfig,
    staging_dataset_id: str,
) -> SqlTransformationRunner:
    """Create the Shopify customers staging transformation."""
    target_table_id = f"{raw_config.project_id}.{staging_dataset_id}.shopify_customers"

    return SqlTransformationRunner(
        client=client,
        sql_path=_SQL_PATH,
        target_table_id=target_table_id,
        template_variables={
            "project_id": raw_config.project_id,
            "raw_dataset_id": raw_config.dataset_id,
            "staging_dataset_id": staging_dataset_id,
        },
    )

"""Factory helpers for BigQuery warehouse components."""

from alpha60.warehouse.bigquery.config import BigQueryConfig
from alpha60.warehouse.bigquery.google_client import GoogleBigQueryClient
from alpha60.warehouse.bigquery.loader import BigQueryLoader
from alpha60.warehouse.bigquery.state_repository import BigQueryStateRepository


def create_bigquery_client(config: BigQueryConfig) -> GoogleBigQueryClient:
    """Create a Google BigQuery client."""
    return GoogleBigQueryClient(config=config)


def create_bigquery_loader(config: BigQueryConfig) -> BigQueryLoader:
    """Create a BigQuery loader using the Google BigQuery client."""
    return BigQueryLoader(
        config=config,
        client=create_bigquery_client(config=config),
    )


def create_bigquery_state_repository(
    config: BigQueryConfig,
) -> BigQueryStateRepository:
    """Create a BigQuery-backed incremental state repository."""
    return BigQueryStateRepository(
        table_id=f"{config.project_id}.{config.dataset_id}.platform_state",
        client=create_bigquery_client(config=config),
    )
"""Composition root for Shopify product ingestion."""

from alpha60.config.settings import Settings
from alpha60.connectors.shopify.auth import ShopifyAuthenticator
from alpha60.connectors.shopify.client import ShopifyClient
from alpha60.jobs.shopify_products import load_shopify_products
from alpha60.state import IncrementalState
from alpha60.warehouse.bigquery.config import BigQueryConfig
from alpha60.warehouse.bigquery.factory import (
    create_bigquery_loader,
    create_bigquery_state_repository,
)
from alpha60.warehouse.types import WarehouseLoadResult, WarehouseLoadStatus


_SHOPIFY_PRODUCTS_JOB_NAME = "shopify-products"
_SHOPIFY_PRODUCTS_CURSOR_FIELD = "updated_at"


def run_shopify_products_ingestion(settings: Settings) -> WarehouseLoadResult:
    """Run the Shopify products ingestion job using runtime settings."""
    authenticator = ShopifyAuthenticator(
        shop_domain=settings.shopify.shop_domain,
        client_id=settings.shopify.client_id,
        client_secret=settings.shopify.client_secret,
    )

    shopify_client = ShopifyClient(
        shop_domain=settings.shopify.shop_domain,
        access_token=authenticator.get_access_token(),
        api_version=settings.shopify.api_version,
    )

    bigquery_config = BigQueryConfig(
        project_id=settings.bigquery.project_id,
        dataset_id=settings.bigquery.dataset_id,
        location=settings.bigquery.location,
    )

    bigquery_loader = create_bigquery_loader(config=bigquery_config)
    state_repository = create_bigquery_state_repository(config=bigquery_config)
    state = state_repository.get_state(_SHOPIFY_PRODUCTS_JOB_NAME)

    job_result = load_shopify_products(
        shopify_client=shopify_client,
        warehouse_loader=bigquery_loader,
        updated_since=state.cursor_value if state is not None else None,
    )

    if (
        job_result.warehouse_result.status == WarehouseLoadStatus.SUCCESS
        and job_result.records_processed > 0
        and job_result.latest_cursor is not None
    ):
        state_repository.save_state(
            IncrementalState(
                job_name=_SHOPIFY_PRODUCTS_JOB_NAME,
                cursor_field=_SHOPIFY_PRODUCTS_CURSOR_FIELD,
                cursor_value=job_result.latest_cursor,
            )
        )

    return job_result.warehouse_result
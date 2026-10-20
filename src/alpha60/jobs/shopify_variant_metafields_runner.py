"""Composition root for Shopify variant metafield ingestion."""

from alpha60.config.settings import Settings
from alpha60.connectors.shopify.auth import ShopifyAuthenticator
from alpha60.connectors.shopify.client import ShopifyClient
from alpha60.jobs.shopify_variant_metafields import (
    load_shopify_variant_metafields,
)
from alpha60.warehouse.bigquery.config import BigQueryConfig
from alpha60.warehouse.bigquery.factory import create_bigquery_loader
from alpha60.warehouse.types import WarehouseLoadResult


def run_shopify_variant_metafields_ingestion(
    settings: Settings,
) -> WarehouseLoadResult:
    """Run Shopify variant metafield ingestion using runtime settings."""
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

    job_result = load_shopify_variant_metafields(
        shopify_client=shopify_client,
        warehouse_loader=bigquery_loader,
    )

    return job_result.warehouse_result

"""Tests for Shopify product ingestion composition."""

from unittest.mock import Mock, patch

from alpha60.config.bigquery import BigQuerySettings
from alpha60.config.settings import Settings
from alpha60.config.shopify import ShopifySettings
from alpha60.jobs.shopify_products_runner import run_shopify_products_ingestion
from alpha60.warehouse.types import WarehouseLoadResult, WarehouseLoadStatus


def test_run_shopify_products_ingestion_wires_dependencies() -> None:
    """The runner builds dependencies from settings and runs the job."""
    settings = Settings(
        environment="test",
        log_level="INFO",
        shopify=ShopifySettings(
            shop_domain="alpha60.myshopify.com",
            access_token="secret",
            api_version="2025-01",
        ),
        bigquery=BigQuerySettings(
            project_id="alpha60-dev",
            dataset_id="raw",
            location="australia-southeast1",
        ),
    )
    expected_result = WarehouseLoadResult(
        table_id="shopify_products",
        status=WarehouseLoadStatus.SUCCESS,
        rows_loaded=1,
    )

    with (
        patch("alpha60.jobs.shopify_products_runner.ShopifyClient") as shopify_client_class,
        patch("alpha60.jobs.shopify_products_runner.create_bigquery_loader") as loader_factory,
        patch(
            "alpha60.jobs.shopify_products_runner.create_bigquery_state_repository"
        ) as state_repository_factory,
        patch("alpha60.jobs.shopify_products_runner.load_shopify_products") as load_job,
    ):
        shopify_client = Mock()
        warehouse_loader = Mock()
        state_repository = Mock()
        shopify_client_class.return_value = shopify_client
        loader_factory.return_value = warehouse_loader
        state_repository_factory.return_value = state_repository
        state_repository.get_state.return_value = None
        load_job.return_value = expected_result

        result = run_shopify_products_ingestion(settings=settings)

    assert result == expected_result

    shopify_client_class.assert_called_once_with(
        shop_domain="alpha60.myshopify.com",
        access_token="secret",
        api_version="2025-01",
    )

    loader_factory.assert_called_once()
    state_repository_factory.assert_called_once()
    state_repository.get_state.assert_called_once_with("shopify-products")
    load_job.assert_called_once_with(
        shopify_client=shopify_client,
        warehouse_loader=warehouse_loader,
        updated_since=None,
    )
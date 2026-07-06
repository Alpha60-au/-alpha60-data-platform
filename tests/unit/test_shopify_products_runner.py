"""Tests for Shopify product ingestion composition."""

from datetime import UTC, datetime
from unittest.mock import Mock, patch

from alpha60.config.bigquery import BigQuerySettings
from alpha60.config.settings import Settings
from alpha60.config.shopify import ShopifySettings
from alpha60.jobs.result import IngestionJobResult
from alpha60.jobs.shopify_products_runner import run_shopify_products_ingestion
from alpha60.state import IncrementalState
from alpha60.warehouse.types import WarehouseLoadResult, WarehouseLoadStatus


def _settings() -> Settings:
    """Create test settings."""
    return Settings(
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


def test_run_shopify_products_ingestion_wires_dependencies() -> None:
    """The runner builds dependencies from settings and runs the job."""
    warehouse_result = WarehouseLoadResult(
        table_id="shopify_products",
        status=WarehouseLoadStatus.SUCCESS,
        rows_loaded=1,
    )
    expected_result = IngestionJobResult(
        warehouse_result=warehouse_result,
        records_processed=1,
        latest_cursor=None,
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

        result = run_shopify_products_ingestion(settings=_settings())

    assert result == warehouse_result

    shopify_client_class.assert_called_once_with(
        shop_domain="alpha60.myshopify.com",
        access_token="secret",
        api_version="2025-01",
    )

    loader_factory.assert_called_once()
    state_repository_factory.assert_called_once()
    state_repository.get_state.assert_called_once_with("shopify-products")
    state_repository.save_state.assert_not_called()
    load_job.assert_called_once_with(
        shopify_client=shopify_client,
        warehouse_loader=warehouse_loader,
        updated_since=None,
    )


def test_run_shopify_products_ingestion_passes_existing_cursor() -> None:
    """The runner passes an existing cursor to the Shopify products job."""
    previous_cursor = datetime(2026, 7, 3, 12, 30, tzinfo=UTC)
    warehouse_result = WarehouseLoadResult(
        table_id="shopify_products",
        status=WarehouseLoadStatus.SUCCESS,
        rows_loaded=0,
    )
    expected_result = IngestionJobResult(
        warehouse_result=warehouse_result,
        records_processed=0,
        latest_cursor=None,
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
        state_repository.get_state.return_value = IncrementalState(
            job_name="shopify-products",
            cursor_field="updated_at",
            cursor_value=previous_cursor,
        )
        load_job.return_value = expected_result

        result = run_shopify_products_ingestion(settings=_settings())

    assert result == warehouse_result
    state_repository.save_state.assert_not_called()
    load_job.assert_called_once_with(
        shopify_client=shopify_client,
        warehouse_loader=warehouse_loader,
        updated_since=previous_cursor,
    )


def test_run_shopify_products_ingestion_saves_cursor_after_successful_load() -> None:
    """The runner saves the latest cursor after a successful load."""
    latest_cursor = datetime(2026, 7, 3, 13, 30, tzinfo=UTC)
    warehouse_result = WarehouseLoadResult(
        table_id="shopify_products",
        status=WarehouseLoadStatus.SUCCESS,
        rows_loaded=1,
    )
    expected_result = IngestionJobResult(
        warehouse_result=warehouse_result,
        records_processed=1,
        latest_cursor=latest_cursor,
    )

    with (
        patch("alpha60.jobs.shopify_products_runner.ShopifyClient") as shopify_client_class,
        patch("alpha60.jobs.shopify_products_runner.create_bigquery_loader") as loader_factory,
        patch(
            "alpha60.jobs.shopify_products_runner.create_bigquery_state_repository"
        ) as state_repository_factory,
        patch("alpha60.jobs.shopify_products_runner.load_shopify_products") as load_job,
    ):
        shopify_client_class.return_value = Mock()
        loader_factory.return_value = Mock()
        state_repository = Mock()
        state_repository_factory.return_value = state_repository
        state_repository.get_state.return_value = None
        load_job.return_value = expected_result

        result = run_shopify_products_ingestion(settings=_settings())

    assert result == warehouse_result
    state_repository.save_state.assert_called_once_with(
        IncrementalState(
            job_name="shopify-products",
            cursor_field="updated_at",
            cursor_value=latest_cursor,
        )
    )


def test_run_shopify_products_ingestion_does_not_save_cursor_after_failed_load() -> None:
    """The runner does not save state when the warehouse load fails."""
    latest_cursor = datetime(2026, 7, 3, 13, 30, tzinfo=UTC)
    warehouse_result = WarehouseLoadResult(
        table_id="shopify_products",
        status=WarehouseLoadStatus.FAILED,
        rows_loaded=0,
        error_message="BigQuery load failed",
    )
    expected_result = IngestionJobResult(
        warehouse_result=warehouse_result,
        records_processed=1,
        latest_cursor=latest_cursor,
    )

    with (
        patch("alpha60.jobs.shopify_products_runner.ShopifyClient"),
        patch("alpha60.jobs.shopify_products_runner.create_bigquery_loader"),
        patch(
            "alpha60.jobs.shopify_products_runner.create_bigquery_state_repository"
        ) as state_repository_factory,
        patch("alpha60.jobs.shopify_products_runner.load_shopify_products") as load_job,
    ):
        state_repository = Mock()
        state_repository_factory.return_value = state_repository
        state_repository.get_state.return_value = None
        load_job.return_value = expected_result

        result = run_shopify_products_ingestion(settings=_settings())

    assert result == warehouse_result
    state_repository.save_state.assert_not_called()
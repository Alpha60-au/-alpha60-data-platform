"""Tests for the daily refresh orchestration runner."""

from collections.abc import Iterator
from unittest.mock import Mock, call, patch

import pytest

from alpha60.pipelines.daily_refresh import (
    DailyRefreshStatus,
    run_daily_refresh,
)
from alpha60.pipelines.dbt_pipeline import (
    DbtBuildResult,
    DbtBuildStatus,
)
from alpha60.transformations.pipeline import TransformationPipelineResult
from alpha60.transformations.result import (
    TransformationResult,
    TransformationStatus,
)
from alpha60.warehouse.types import WarehouseLoadResult, WarehouseLoadStatus


@pytest.fixture(autouse=True)
def successful_dbt_build() -> Iterator[Mock]:
    """Provide a successful dbt build by default."""
    with patch(
        "alpha60.pipelines.daily_refresh.run_dbt_build",
        return_value=DbtBuildResult(
            status=DbtBuildStatus.SUCCESS,
            return_code=0,
            stdout="Completed successfully",
            stderr="",
        ),
    ) as run_dbt:
        yield run_dbt


@pytest.fixture(autouse=True)
def successful_transformation_pipeline() -> Iterator[Mock]:
    """Provide a successful Shopify transformation pipeline by default."""
    pipeline = Mock()
    pipeline.run.return_value = TransformationPipelineResult(
        status=TransformationStatus.SUCCESS,
        results=[
            TransformationResult(
                target_table_id="alpha60-data-platform.stg.shopify_products",
                status=TransformationStatus.SUCCESS,
            )
        ],
    )

    with patch(
        "alpha60.pipelines.daily_refresh.create_shopify_transformation_pipeline",
        return_value=pipeline,
    ):
        yield pipeline


@pytest.fixture(autouse=True)
def successful_customer_ingestion() -> Iterator[Mock]:
    """Provide a successful Shopify customer ingestion by default."""
    with patch(
        "alpha60.pipelines.daily_refresh.run_shopify_customers_ingestion",
        return_value=WarehouseLoadResult(
            table_id="shopify_customers",
            status=WarehouseLoadStatus.SUCCESS,
            rows_loaded=6,
        ),
    ) as run_customers:
        yield run_customers


def _successful_load(table_id: str, rows_loaded: int) -> WarehouseLoadResult:
    """Create a successful warehouse load result."""
    return WarehouseLoadResult(
        table_id=table_id,
        status=WarehouseLoadStatus.SUCCESS,
        rows_loaded=rows_loaded,
    )


def _failed_load(table_id: str, error_message: str) -> WarehouseLoadResult:
    """Create a failed warehouse load result."""
    return WarehouseLoadResult(
        table_id=table_id,
        status=WarehouseLoadStatus.FAILED,
        rows_loaded=0,
        error_message=error_message,
    )


def test_daily_refresh_runs_ingestions_in_order() -> None:
    """The daily refresh runs all Shopify ingestions sequentially."""
    settings = Mock()

    products_result = _successful_load("shopify_products", 3)
    orders_result = _successful_load("shopify_orders", 4)
    customers_result = _successful_load("shopify_customers", 6)
    inventory_result = _successful_load("shopify_inventory_levels", 5)

    execution_order: list[str] = []

    def run_products_side_effect(**_: object) -> WarehouseLoadResult:
        execution_order.append("products")
        return products_result

    def run_orders_side_effect(**_: object) -> WarehouseLoadResult:
        execution_order.append("orders")
        return orders_result

    def run_customers_side_effect(**_: object) -> WarehouseLoadResult:
        execution_order.append("customers")
        return customers_result

    def run_inventory_side_effect(**_: object) -> WarehouseLoadResult:
        execution_order.append("inventory")
        return inventory_result

    with (
        patch(
            "alpha60.pipelines.daily_refresh.run_shopify_products_ingestion"
        ) as run_products,
        patch(
            "alpha60.pipelines.daily_refresh.run_shopify_orders_ingestion"
        ) as run_orders,
        patch(
            "alpha60.pipelines.daily_refresh.run_shopify_customers_ingestion"
        ) as run_customers,
        patch(
            "alpha60.pipelines.daily_refresh.run_shopify_inventory_levels_ingestion"
        ) as run_inventory,
    ):
        run_products.side_effect = run_products_side_effect
        run_orders.side_effect = run_orders_side_effect
        run_customers.side_effect = run_customers_side_effect
        run_inventory.side_effect = run_inventory_side_effect

        result = run_daily_refresh(settings=settings)

    assert execution_order == ["products", "orders", "customers", "inventory"]
    assert result.status == DailyRefreshStatus.SUCCESS
    assert result.products_result == products_result
    assert result.orders_result == orders_result
    assert result.customers_result == customers_result
    assert result.inventory_levels_result == inventory_result
    assert result.failed_stage is None
    assert result.error_message is None

    run_products.assert_called_once_with(settings=settings)
    run_orders.assert_called_once_with(settings=settings, max_pages=None)
    run_customers.assert_called_once_with(settings=settings)
    run_inventory.assert_called_once_with(settings=settings)


def test_daily_refresh_stops_when_products_fail() -> None:
    """The daily refresh stops immediately when products ingestion fails."""
    settings = Mock()
    products_result = _failed_load(
        "shopify_products",
        "Products load failed",
    )

    with (
        patch(
            "alpha60.pipelines.daily_refresh.run_shopify_products_ingestion",
            return_value=products_result,
        ) as run_products,
        patch(
            "alpha60.pipelines.daily_refresh.run_shopify_orders_ingestion"
        ) as run_orders,
        patch(
            "alpha60.pipelines.daily_refresh.run_shopify_inventory_levels_ingestion"
        ) as run_inventory,
    ):
        result = run_daily_refresh(settings=settings)

    assert result.status == DailyRefreshStatus.FAILED
    assert result.products_result == products_result
    assert result.orders_result is None
    assert result.inventory_levels_result is None
    assert result.failed_stage == "shopify-products"
    assert result.error_message == "Products load failed"

    run_products.assert_called_once_with(settings=settings)
    run_orders.assert_not_called()
    run_inventory.assert_not_called()


def test_daily_refresh_stops_when_orders_fail() -> None:
    """The daily refresh stops before inventory when orders ingestion fails."""
    settings = Mock()

    products_result = _successful_load("shopify_products", 3)
    orders_result = _failed_load(
        "shopify_orders",
        "Orders load failed",
    )

    with (
        patch(
            "alpha60.pipelines.daily_refresh.run_shopify_products_ingestion",
            return_value=products_result,
        ) as run_products,
        patch(
            "alpha60.pipelines.daily_refresh.run_shopify_orders_ingestion",
            return_value=orders_result,
        ) as run_orders,
        patch(
            "alpha60.pipelines.daily_refresh.run_shopify_inventory_levels_ingestion"
        ) as run_inventory,
    ):
        result = run_daily_refresh(settings=settings)

    assert result.status == DailyRefreshStatus.FAILED
    assert result.products_result == products_result
    assert result.orders_result == orders_result
    assert result.inventory_levels_result is None
    assert result.failed_stage == "shopify-orders"
    assert result.error_message == "Orders load failed"

    run_products.assert_called_once_with(settings=settings)
    run_orders.assert_called_once_with(settings=settings, max_pages=None)
    run_inventory.assert_not_called()


def test_daily_refresh_reports_inventory_failure() -> None:
    """The daily refresh reports an inventory ingestion failure."""
    settings = Mock()

    products_result = _successful_load("shopify_products", 3)
    orders_result = _successful_load("shopify_orders", 4)
    inventory_result = _failed_load(
        "shopify_inventory_levels",
        "Inventory load failed",
    )

    with (
        patch(
            "alpha60.pipelines.daily_refresh.run_shopify_products_ingestion",
            return_value=products_result,
        ) as run_products,
        patch(
            "alpha60.pipelines.daily_refresh.run_shopify_orders_ingestion",
            return_value=orders_result,
        ) as run_orders,
        patch(
            "alpha60.pipelines.daily_refresh.run_shopify_inventory_levels_ingestion",
            return_value=inventory_result,
        ) as run_inventory,
    ):
        result = run_daily_refresh(settings=settings)

    assert result.status == DailyRefreshStatus.FAILED
    assert result.products_result == products_result
    assert result.orders_result == orders_result
    assert result.inventory_levels_result == inventory_result
    assert result.failed_stage == "shopify-inventory-levels"
    assert result.error_message == "Inventory load failed"

    assert [mock.call_count for mock in (run_products, run_orders, run_inventory)] == [
        1,
        1,
        1,
    ]


def test_daily_refresh_passes_orders_max_pages() -> None:
    """The daily refresh passes an optional order page limit."""
    settings = Mock()

    with (
        patch(
            "alpha60.pipelines.daily_refresh.run_shopify_products_ingestion",
            return_value=_successful_load("shopify_products", 3),
        ),
        patch(
            "alpha60.pipelines.daily_refresh.run_shopify_orders_ingestion",
            return_value=_successful_load("shopify_orders", 4),
        ) as run_orders,
        patch(
            "alpha60.pipelines.daily_refresh.run_shopify_inventory_levels_ingestion",
            return_value=_successful_load("shopify_inventory_levels", 5),
        ),
    ):
        result = run_daily_refresh(
            settings=settings,
            orders_max_pages=2,
        )

    assert result.status == DailyRefreshStatus.SUCCESS
    assert run_orders.call_args_list == [
        call(settings=settings, max_pages=2),
    ]


def test_daily_refresh_reports_transformation_failure(
    successful_transformation_pipeline: Mock,
) -> None:
    """The daily refresh fails when the Shopify staging pipeline fails."""
    settings = Mock()

    transformation_result = TransformationPipelineResult(
        status=TransformationStatus.FAILED,
        results=[
            TransformationResult(
                target_table_id="alpha60-data-platform.stg.shopify_orders",
                status=TransformationStatus.FAILED,
                error_message="Transformation query failed",
            )
        ],
    )
    successful_transformation_pipeline.run.return_value = transformation_result

    with (
        patch(
            "alpha60.pipelines.daily_refresh.run_shopify_products_ingestion",
            return_value=_successful_load("shopify_products", 3),
        ),
        patch(
            "alpha60.pipelines.daily_refresh.run_shopify_orders_ingestion",
            return_value=_successful_load("shopify_orders", 4),
        ),
        patch(
            "alpha60.pipelines.daily_refresh.run_shopify_inventory_levels_ingestion",
            return_value=_successful_load("shopify_inventory_levels", 5),
        ),
    ):
        result = run_daily_refresh(settings=settings)

    assert result.status == DailyRefreshStatus.FAILED
    assert result.failed_stage == "shopify-transformations"
    assert result.error_message == "Transformation query failed"
    assert result.transformation_result == transformation_result
    successful_transformation_pipeline.run.assert_called_once_with(
        settings=settings
    )

"""Daily data refresh orchestration for the ALPHA60 Data Platform."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from alpha60.config.settings import Settings
from alpha60.core.logging import get_logger
from alpha60.jobs.shopify_inventory_levels_runner import (
    run_shopify_inventory_levels_ingestion,
)
from alpha60.jobs.shopify_orders_runner import run_shopify_orders_ingestion
from alpha60.jobs.shopify_products_runner import run_shopify_products_ingestion
from alpha60.transformations.pipeline import TransformationPipelineResult
from alpha60.transformations.result import TransformationStatus
from alpha60.transformations.shopify_pipeline import (
    create_shopify_transformation_pipeline,
)
from alpha60.warehouse.types import WarehouseLoadResult, WarehouseLoadStatus


logger = get_logger(__name__)


class DailyRefreshStatus(StrEnum):
    """Overall status of a daily refresh."""

    SUCCESS = "success"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class DailyRefreshResult:
    """Result of the daily ingestion and staging refresh."""

    status: DailyRefreshStatus
    products_result: WarehouseLoadResult | None = None
    orders_result: WarehouseLoadResult | None = None
    inventory_levels_result: WarehouseLoadResult | None = None
    transformation_result: TransformationPipelineResult | None = None
    failed_stage: str | None = None
    error_message: str | None = None


def _failed_ingestion_result(
    *,
    stage: str,
    result: WarehouseLoadResult,
    products_result: WarehouseLoadResult | None = None,
    orders_result: WarehouseLoadResult | None = None,
    inventory_levels_result: WarehouseLoadResult | None = None,
) -> DailyRefreshResult:
    """Build a failed daily refresh result for an ingestion stage."""
    return DailyRefreshResult(
        status=DailyRefreshStatus.FAILED,
        products_result=products_result,
        orders_result=orders_result,
        inventory_levels_result=inventory_levels_result,
        failed_stage=stage,
        error_message=result.error_message,
    )


def run_daily_refresh(
    *,
    settings: Settings,
    orders_max_pages: int | None = None,
) -> DailyRefreshResult:
    """Run the daily Shopify refresh in dependency order."""
    logger.info("Daily refresh started")

    logger.info("Daily refresh stage started", extra={"stage": "shopify-products"})
    products_result = run_shopify_products_ingestion(settings=settings)

    if products_result.status != WarehouseLoadStatus.SUCCESS:
        logger.error(
            "Daily refresh stage failed",
            extra={
                "stage": "shopify-products",
                "error_message": products_result.error_message,
            },
        )
        return _failed_ingestion_result(
            stage="shopify-products",
            result=products_result,
            products_result=products_result,
        )

    logger.info(
        "Daily refresh stage completed",
        extra={
            "stage": "shopify-products",
            "rows_loaded": products_result.rows_loaded,
        },
    )

    logger.info("Daily refresh stage started", extra={"stage": "shopify-orders"})
    orders_result = run_shopify_orders_ingestion(
        settings=settings,
        max_pages=orders_max_pages,
    )

    if orders_result.status != WarehouseLoadStatus.SUCCESS:
        logger.error(
            "Daily refresh stage failed",
            extra={
                "stage": "shopify-orders",
                "error_message": orders_result.error_message,
            },
        )
        return _failed_ingestion_result(
            stage="shopify-orders",
            result=orders_result,
            products_result=products_result,
            orders_result=orders_result,
        )

    logger.info(
        "Daily refresh stage completed",
        extra={
            "stage": "shopify-orders",
            "rows_loaded": orders_result.rows_loaded,
        },
    )

    logger.info(
        "Daily refresh stage started",
        extra={"stage": "shopify-inventory-levels"},
    )
    inventory_levels_result = run_shopify_inventory_levels_ingestion(
        settings=settings
    )

    if inventory_levels_result.status != WarehouseLoadStatus.SUCCESS:
        logger.error(
            "Daily refresh stage failed",
            extra={
                "stage": "shopify-inventory-levels",
                "error_message": inventory_levels_result.error_message,
            },
        )
        return _failed_ingestion_result(
            stage="shopify-inventory-levels",
            result=inventory_levels_result,
            products_result=products_result,
            orders_result=orders_result,
            inventory_levels_result=inventory_levels_result,
        )

    logger.info(
        "Daily refresh stage completed",
        extra={
            "stage": "shopify-inventory-levels",
            "rows_loaded": inventory_levels_result.rows_loaded,
        },
    )

    logger.info(
        "Daily refresh stage started",
        extra={"stage": "shopify-transformations"},
    )
    transformation_pipeline = create_shopify_transformation_pipeline()
    transformation_result = transformation_pipeline.run(settings=settings)

    if transformation_result.status != TransformationStatus.SUCCESS:
        failed_transformation = transformation_result.results[-1]
        logger.error(
            "Daily refresh stage failed",
            extra={
                "stage": "shopify-transformations",
                "target_table_id": failed_transformation.target_table_id,
                "error_message": failed_transformation.error_message,
            },
        )
        return DailyRefreshResult(
            status=DailyRefreshStatus.FAILED,
            products_result=products_result,
            orders_result=orders_result,
            inventory_levels_result=inventory_levels_result,
            transformation_result=transformation_result,
            failed_stage="shopify-transformations",
            error_message=failed_transformation.error_message,
        )

    logger.info(
        "Daily refresh stage completed",
        extra={
            "stage": "shopify-transformations",
            "transformations_completed": len(transformation_result.results),
        },
    )
    logger.info("Daily refresh completed successfully")

    return DailyRefreshResult(
        status=DailyRefreshStatus.SUCCESS,
        products_result=products_result,
        orders_result=orders_result,
        inventory_levels_result=inventory_levels_result,
        transformation_result=transformation_result,
    )

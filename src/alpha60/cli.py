"""Command line interface for the ALPHA60 Data Platform."""

from collections.abc import Sequence
import argparse

from alpha60.config import load_settings
from alpha60.core.logging import configure_logging, get_logger
from alpha60.jobs.shopify_customers_runner import run_shopify_customers_ingestion
from alpha60.pipelines.daily_refresh import (
    DailyRefreshStatus,
    run_daily_refresh,
)
from alpha60.jobs.shopify_inventory_levels_runner import run_shopify_inventory_levels_ingestion
from alpha60.jobs.shopify_locations_runner import run_shopify_locations_ingestion
from alpha60.jobs.shopify_orders_runner import run_shopify_orders_ingestion
from alpha60.jobs.shopify_products_runner import run_shopify_products_ingestion
from alpha60.operations.health import (
    HealthCheckResult,
    HealthStatus,
    check_bigquery,
    check_configuration,
    check_shopify,
)
from alpha60.transformations.result import TransformationStatus
from alpha60.transformations.shopify_order_lines_runner import (
    run_shopify_order_lines_staging_transformation,
)
from alpha60.transformations.shopify_orders_runner import (
    run_shopify_orders_staging_transformation,
)
from alpha60.transformations.shopify_pipeline import (
    create_shopify_transformation_pipeline,
)
from alpha60.transformations.shopify_product_variants_runner import (
    run_shopify_product_variants_staging_transformation,
)
from alpha60.transformations.shopify_products_runner import (
    run_shopify_products_staging_transformation,
)
from alpha60.transformations.shopify_customers_runner import (
    run_shopify_customers_staging_transformation,
)
from alpha60.warehouse.types import WarehouseLoadStatus


logger = get_logger(__name__)


def build_parser() -> argparse.ArgumentParser:
    """Build the ALPHA60 command line parser."""
    parser = argparse.ArgumentParser(
        prog="alpha60",
        description="ALPHA60 operational data platform",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest_parser = subparsers.add_parser(
        "ingest",
        help="Run ingestion jobs",
    )

    ingest_subparsers = ingest_parser.add_subparsers(
        dest="ingestion_job",
        required=True,
    )

    ingest_subparsers.add_parser(
        "shopify-products",
        help="Load Shopify products into BigQuery",
    )

    ingest_subparsers.add_parser(
        "shopify-locations",
        help="Load Shopify locations into BigQuery",
    )

    ingest_subparsers.add_parser(
        "shopify-inventory-levels",
        help="Load Shopify inventory levels into BigQuery",
    )

    shopify_customers_parser = ingest_subparsers.add_parser(
        "shopify-customers",
        help="Load Shopify customers into BigQuery",
    )
    shopify_customers_parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="Maximum number of Shopify customer pages to fetch.",
    )

    shopify_orders_parser = ingest_subparsers.add_parser(
        "shopify-orders",
        help="Load Shopify orders into BigQuery",
    )
    shopify_orders_parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="Maximum number of Shopify order pages to fetch.",
    )

    refresh_parser = subparsers.add_parser(
        "refresh",
        help="Run coordinated data refresh workflows",
    )

    refresh_subparsers = refresh_parser.add_subparsers(
        dest="refresh_job",
        required=True,
    )

    daily_refresh_parser = refresh_subparsers.add_parser(
        "daily",
        help="Refresh Shopify products, orders, and inventory levels",
    )
    daily_refresh_parser.add_argument(
        "--orders-max-pages",
        type=int,
        default=None,
        help="Maximum number of Shopify order pages to fetch.",
    )

    transform_parser = subparsers.add_parser(
        "transform",
        help="Run warehouse transformations",
    )

    transform_subparsers = transform_parser.add_subparsers(
        dest="transformation_job",
        required=True,
    )

    shopify_orders_transform_parser = transform_subparsers.add_parser(
        "shopify-orders",
        help="Build the Shopify orders staging table",
    )
    shopify_orders_transform_parser.add_argument(
        "--staging-dataset",
        default=None,
        help="Override the configured BigQuery dataset for staging tables.",
    )

    shopify_order_lines_transform_parser = transform_subparsers.add_parser(
        "shopify-order-lines",
        help="Build the Shopify order lines staging table",
    )
    shopify_order_lines_transform_parser.add_argument(
        "--staging-dataset",
        default=None,
        help="Override the configured BigQuery dataset for staging tables.",
    )

    shopify_products_transform_parser = transform_subparsers.add_parser(
        "shopify-products",
        help="Build the Shopify products staging table",
    )
    shopify_products_transform_parser.add_argument(
        "--staging-dataset",
        default=None,
        help="Override the configured BigQuery dataset for staging tables.",
    )

    shopify_product_variants_transform_parser = transform_subparsers.add_parser(
        "shopify-product-variants",
        help="Build the Shopify product variants staging table",
    )
    shopify_product_variants_transform_parser.add_argument(
        "--staging-dataset",
        default=None,
        help="Override the configured BigQuery dataset for staging tables.",
    )

    shopify_customers_transform_parser = transform_subparsers.add_parser(
        "shopify-customers",
        help="Build the Shopify customers staging table",
    )
    shopify_customers_transform_parser.add_argument(
        "--staging-dataset",
        default=None,
        help="Override the configured BigQuery dataset for staging tables.",
    )

    transform_all_parser = transform_subparsers.add_parser(
        "all",
        help="Run the complete Shopify transformation pipeline",
    )
    transform_all_parser.add_argument(
        "--staging-dataset",
        default=None,
        help="Override the configured BigQuery dataset for staging tables.",
    )

    test_parser = subparsers.add_parser(
        "test",
        help="Run operational health checks",
    )

    test_subparsers = test_parser.add_subparsers(
        dest="health_check",
        required=True,
    )

    test_subparsers.add_parser(
        "config",
        help="Validate runtime configuration",
    )

    test_subparsers.add_parser(
        "shopify",
        help="Validate Shopify connectivity",
    )

    test_subparsers.add_parser(
        "bigquery",
        help="Validate BigQuery connectivity",
    )

    test_subparsers.add_parser(
        "all",
        help="Run all operational health checks",
    )

    return parser


def print_health_result(result: HealthCheckResult) -> None:
    """Print a health check result."""
    print(f"{result.name}: {result.status.value} - {result.message}")


def _print_load_result(load_result) -> None:
    """Print an ingestion load result."""
    print(
        f"Loaded {load_result.rows_loaded} rows into "
        f"{load_result.table_id} "
        f"with status {load_result.status.value}."
    )

    if load_result.error_message is not None:
        print()
        print("Error details:")
        print(load_result.error_message)

def _print_transformation_result(result) -> None:
    """Print a transformation result."""
    print(f"Transformed {result.target_table_id} with status {result.status.value}.")


def main(argv: Sequence[str] | None = None) -> int:
    """Run the ALPHA60 command line interface."""
    configure_logging()

    parser = build_parser()
    args = parser.parse_args(argv)

    logger.info(
        "CLI command started",
        extra={
            "command": args.command,
        },
    )

    if args.command == "refresh" and args.refresh_job == "daily":
        settings = load_settings()
        refresh_result = run_daily_refresh(
            settings=settings,
            orders_max_pages=args.orders_max_pages,
        )

        if refresh_result.status == DailyRefreshStatus.SUCCESS:
            products_rows = (
                refresh_result.products_result.rows_loaded
                if refresh_result.products_result is not None
                else 0
            )
            orders_rows = (
                refresh_result.orders_result.rows_loaded
                if refresh_result.orders_result is not None
                else 0
            )
            inventory_rows = (
                refresh_result.inventory_levels_result.rows_loaded
                if refresh_result.inventory_levels_result is not None
                else 0
            )

            print(
                "Daily refresh completed successfully: "
                f"products={products_rows}, "
                f"orders={orders_rows}, "
                f"inventory_levels={inventory_rows}."
            )
            return 0

        print(
            "Daily refresh failed at "
            f"{refresh_result.failed_stage}: "
            f"{refresh_result.error_message or 'Unknown error'}"
        )
        return 1

    if args.command == "ingest" and args.ingestion_job == "shopify-inventory-levels":
        settings = load_settings()
        load_result = run_shopify_inventory_levels_ingestion(settings=settings)

        _print_load_result(load_result)

        logger.info(
            "Shopify inventory levels ingestion completed",
            extra={
                "table_id": load_result.table_id,
                "rows_loaded": load_result.rows_loaded,
                "status": load_result.status.value,
            },
        )

        return 0 if load_result.status == WarehouseLoadStatus.SUCCESS else 1

    if args.command == "ingest" and args.ingestion_job == "shopify-locations":
        settings = load_settings()
        load_result = run_shopify_locations_ingestion(settings=settings)

        _print_load_result(load_result)

        logger.info(
            "Shopify locations ingestion completed",
            extra={
                "table_id": load_result.table_id,
                "rows_loaded": load_result.rows_loaded,
                "status": load_result.status.value,
            },
        )

        return 0 if load_result.status == WarehouseLoadStatus.SUCCESS else 1

    if args.command == "ingest" and args.ingestion_job == "shopify-customers":
        settings = load_settings()
        load_result = run_shopify_customers_ingestion(
            settings=settings,
            max_pages=args.max_pages,
        )

        _print_load_result(load_result)

        logger.info(
            "Shopify customers ingestion completed",
            extra={
                "table_id": load_result.table_id,
                "rows_loaded": load_result.rows_loaded,
                "status": load_result.status.value,
            },
        )

        return 0 if load_result.status == WarehouseLoadStatus.SUCCESS else 1

    if args.command == "ingest" and args.ingestion_job == "shopify-products":
        settings = load_settings()
        load_result = run_shopify_products_ingestion(settings=settings)

        _print_load_result(load_result)

        logger.info(
            "Shopify products ingestion completed",
            extra={
                "table_id": load_result.table_id,
                "rows_loaded": load_result.rows_loaded,
                "status": load_result.status.value,
            },
        )

        return 0 if load_result.status == WarehouseLoadStatus.SUCCESS else 1

    if args.command == "ingest" and args.ingestion_job == "shopify-orders":
        settings = load_settings()
        load_result = run_shopify_orders_ingestion(
            settings=settings,
            max_pages=args.max_pages,
        )

        _print_load_result(load_result)

        logger.info(
            "Shopify orders ingestion completed",
            extra={
                "table_id": load_result.table_id,
                "rows_loaded": load_result.rows_loaded,
                "status": load_result.status.value,
            },
        )

        return 0 if load_result.status == WarehouseLoadStatus.SUCCESS else 1

    if args.command == "transform" and args.transformation_job == "shopify-orders":
        settings = load_settings()
        transformation_result = run_shopify_orders_staging_transformation(
            settings=settings,
            staging_dataset_id=args.staging_dataset,
        )

        _print_transformation_result(transformation_result)

        logger.info(
            "Shopify orders staging transformation completed",
            extra={
                "target_table_id": transformation_result.target_table_id,
                "status": transformation_result.status.value,
                "error_message": transformation_result.error_message,
            },
        )

        return 0 if transformation_result.status == TransformationStatus.SUCCESS else 1

    if args.command == "transform" and args.transformation_job == "shopify-order-lines":
        settings = load_settings()
        transformation_result = run_shopify_order_lines_staging_transformation(
            settings=settings,
            staging_dataset_id=args.staging_dataset,
        )

        _print_transformation_result(transformation_result)

        logger.info(
            "Shopify order lines staging transformation completed",
            extra={
                "target_table_id": transformation_result.target_table_id,
                "status": transformation_result.status.value,
                "error_message": transformation_result.error_message,
            },
        )

        return 0 if transformation_result.status == TransformationStatus.SUCCESS else 1

    if args.command == "transform" and args.transformation_job == "shopify-products":
        settings = load_settings()
        transformation_result = run_shopify_products_staging_transformation(
            settings=settings,
            staging_dataset_id=args.staging_dataset,
        )

        _print_transformation_result(transformation_result)

        logger.info(
            "Shopify products staging transformation completed",
            extra={
                "target_table_id": transformation_result.target_table_id,
                "status": transformation_result.status.value,
                "error_message": transformation_result.error_message,
            },
        )

        return 0 if transformation_result.status == TransformationStatus.SUCCESS else 1

    if (
        args.command == "transform"
        and args.transformation_job == "shopify-product-variants"
    ):
        settings = load_settings()
        transformation_result = run_shopify_product_variants_staging_transformation(
            settings=settings,
            staging_dataset_id=args.staging_dataset,
        )

        _print_transformation_result(transformation_result)

        logger.info(
            "Shopify product variants staging transformation completed",
            extra={
                "target_table_id": transformation_result.target_table_id,
                "status": transformation_result.status.value,
                "error_message": transformation_result.error_message,
            },
        )

        return 0 if transformation_result.status == TransformationStatus.SUCCESS else 1

    if args.command == "transform" and args.transformation_job == "shopify-customers":
        settings = load_settings()
        transformation_result = run_shopify_customers_staging_transformation(
            settings=settings,
            staging_dataset_id=args.staging_dataset,
        )

        _print_transformation_result(transformation_result)

        logger.info(
            "Shopify customers staging transformation completed",
            extra={
                "target_table_id": transformation_result.target_table_id,
                "status": transformation_result.status.value,
                "error_message": transformation_result.error_message,
            },
        )

        return 0 if transformation_result.status == TransformationStatus.SUCCESS else 1

    if args.command == "transform" and args.transformation_job == "all":
        settings = load_settings()
        pipeline = create_shopify_transformation_pipeline()
        pipeline_result = pipeline.run(
            settings=settings,
            staging_dataset_id=args.staging_dataset,
        )

        for result in pipeline_result.results:
            _print_transformation_result(result)

        logger.info(
            "Shopify transformation pipeline completed",
            extra={
                "status": pipeline_result.status.value,
                "steps": [
                    {
                        "target_table_id": result.target_table_id,
                        "status": result.status.value,
                    }
                    for result in pipeline_result.results
                ],
            },
        )

        return 0 if pipeline_result.status == TransformationStatus.SUCCESS else 1

    if args.command == "test" and args.health_check == "config":
        settings = load_settings()
        health_result = check_configuration(settings=settings)

        print_health_result(health_result)

        logger.info(
            "Configuration health check completed",
            extra={
                "status": health_result.status.value,
                "health_message": health_result.message,
            },
        )

        return 0 if health_result.status == HealthStatus.PASS else 1

    if args.command == "test" and args.health_check == "shopify":
        settings = load_settings()
        health_result = check_shopify(settings=settings)

        print_health_result(health_result)

        logger.info(
            "Shopify health check completed",
            extra={
                "status": health_result.status.value,
                "health_message": health_result.message,
            },
        )

        return 0 if health_result.status == HealthStatus.PASS else 1

    if args.command == "test" and args.health_check == "bigquery":
        settings = load_settings()
        health_result = check_bigquery(settings=settings)

        print_health_result(health_result)

        logger.info(
            "BigQuery health check completed",
            extra={
                "status": health_result.status.value,
                "health_message": health_result.message,
            },
        )

        return 0 if health_result.status == HealthStatus.PASS else 1

    if args.command == "test" and args.health_check == "all":
        settings = load_settings()
        health_results = [
            check_configuration(settings=settings),
            check_shopify(settings=settings),
            check_bigquery(settings=settings),
        ]

        for health_result in health_results:
            print_health_result(health_result)

        all_passed = all(result.status == HealthStatus.PASS for result in health_results)

        logger.info(
            "All health checks completed",
            extra={
                "status": HealthStatus.PASS.value if all_passed else HealthStatus.FAIL.value,
                "checks": [
                    {
                        "name": result.name,
                        "status": result.status.value,
                        "health_message": result.message,
                    }
                    for result in health_results
                ],
            },
        )

        return 0 if all_passed else 1

    parser.error("Unsupported command")
    return 2

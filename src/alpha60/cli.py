"""Command line interface for the ALPHA60 Data Platform."""

from collections.abc import Sequence
import argparse

from alpha60.config import load_settings
from alpha60.core.logging import configure_logging, get_logger
from alpha60.jobs.shopify_orders_runner import run_shopify_orders_ingestion
from alpha60.jobs.shopify_products_runner import run_shopify_products_ingestion
from alpha60.operations.health import (
    HealthCheckResult,
    HealthStatus,
    check_bigquery,
    check_configuration,
    check_shopify,
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
        "shopify-orders",
        help="Load Shopify orders into BigQuery",
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
        load_result = run_shopify_orders_ingestion(settings=settings)

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

        if all_passed:
            return 0

        return 1

    parser.error("Unsupported command")
    return 2
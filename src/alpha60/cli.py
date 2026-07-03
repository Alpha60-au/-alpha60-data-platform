"""Command line interface for the ALPHA60 Data Platform."""

from collections.abc import Sequence
import argparse

from alpha60.config import load_settings
from alpha60.jobs.shopify_products_runner import run_shopify_products_ingestion
from alpha60.operations.health import (
    HealthCheckResult,
    HealthStatus,
    check_bigquery,
    check_configuration,
    check_shopify,
)
from alpha60.warehouse.types import WarehouseLoadStatus


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


def main(argv: Sequence[str] | None = None) -> int:
    """Run the ALPHA60 command line interface."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "ingest" and args.ingestion_job == "shopify-products":
        settings = load_settings()
        load_result = run_shopify_products_ingestion(settings=settings)

        print(
            f"Loaded {load_result.rows_loaded} rows into "
            f"{load_result.table_id} "
            f"with status {load_result.status.value}."
        )

        return 0 if load_result.status == WarehouseLoadStatus.SUCCESS else 1

    if args.command == "test" and args.health_check == "config":
        settings = load_settings()
        health_result = check_configuration(settings=settings)

        print_health_result(health_result)

        return 0 if health_result.status == HealthStatus.PASS else 1

    if args.command == "test" and args.health_check == "shopify":
        settings = load_settings()
        health_result = check_shopify(settings=settings)

        print_health_result(health_result)

        return 0 if health_result.status == HealthStatus.PASS else 1

    if args.command == "test" and args.health_check == "bigquery":
        settings = load_settings()
        health_result = check_bigquery(settings=settings)

        print_health_result(health_result)

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

        if all(result.status == HealthStatus.PASS for result in health_results):
            return 0

        return 1

    parser.error("Unsupported command")
    return 2
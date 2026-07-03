"""Command line interface for the ALPHA60 Data Platform."""

from collections.abc import Sequence
import argparse

from alpha60.config import load_settings
from alpha60.jobs.shopify_products_runner import run_shopify_products_ingestion
from alpha60.operations.health import (
    HealthStatus,
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

    return parser


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

        print(
            f"{health_result.name}: "
            f"{health_result.status.value} - "
            f"{health_result.message}"
        )

        return 0 if health_result.status == HealthStatus.PASS else 1

    if args.command == "test" and args.health_check == "shopify":
        settings = load_settings()
        health_result = check_shopify(settings=settings)

        print(
            f"{health_result.name}: "
            f"{health_result.status.value} - "
            f"{health_result.message}"
        )

        return 0 if health_result.status == HealthStatus.PASS else 1

    parser.error("Unsupported command")
    return 2
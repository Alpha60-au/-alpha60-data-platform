"""Command line interface for the ALPHA60 Data Platform."""

from collections.abc import Sequence
import argparse

from alpha60.config import load_settings
from alpha60.jobs.shopify_products_runner import run_shopify_products_ingestion
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

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the ALPHA60 command line interface."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "ingest" and args.ingestion_job == "shopify-products":
        settings = load_settings()
        result = run_shopify_products_ingestion(settings=settings)

        print(
            f"Loaded {result.rows_loaded} rows into "
            f"{result.table_id} "
            f"with status {result.status.value}."
        )

        if result.status == WarehouseLoadStatus.SUCCESS:
            return 0

        return 1

    parser.error("Unsupported command")
    return 2
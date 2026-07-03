"""Tests for the ALPHA60 command line interface."""

from unittest.mock import patch

from alpha60.cli import main
from alpha60.warehouse.types import WarehouseLoadResult, WarehouseLoadStatus


def test_cli_runs_shopify_products_ingestion(capsys) -> None:
    """The CLI runs the Shopify products ingestion job."""
    result = WarehouseLoadResult(
        table_id="shopify_products",
        status=WarehouseLoadStatus.SUCCESS,
        rows_loaded=3,
    )

    with (
        patch("alpha60.cli.load_settings") as load_settings,
        patch("alpha60.cli.run_shopify_products_ingestion") as run_job,
    ):
        settings = object()
        load_settings.return_value = settings
        run_job.return_value = result

        exit_code = main(["ingest", "shopify-products"])

    assert exit_code == 0
    run_job.assert_called_once_with(settings=settings)

    captured = capsys.readouterr()
    assert "Loaded 3 rows into shopify_products with status success." in captured.out
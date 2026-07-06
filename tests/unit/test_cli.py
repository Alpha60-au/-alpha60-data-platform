"""Tests for the ALPHA60 command line interface."""

from unittest.mock import patch

from alpha60.cli import main
from alpha60.operations.health import HealthCheckResult, HealthStatus
from alpha60.warehouse.types import WarehouseLoadResult, WarehouseLoadStatus


def test_cli_runs_shopify_products_ingestion(capsys) -> None:
    """The CLI runs the Shopify products ingestion job."""
    load_result = WarehouseLoadResult(
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
        run_job.return_value = load_result

        exit_code = main(["ingest", "shopify-products"])

    assert exit_code == 0
    run_job.assert_called_once_with(settings=settings)

    captured = capsys.readouterr()
    assert "Loaded 3 rows into shopify_products with status success." in captured.out


def test_cli_runs_shopify_orders_ingestion(capsys) -> None:
    """The CLI runs the Shopify orders ingestion job."""
    load_result = WarehouseLoadResult(
        table_id="shopify_orders",
        status=WarehouseLoadStatus.SUCCESS,
        rows_loaded=4,
    )

    with (
        patch("alpha60.cli.load_settings") as load_settings,
        patch("alpha60.cli.run_shopify_orders_ingestion") as run_job,
    ):
        settings = object()
        load_settings.return_value = settings
        run_job.return_value = load_result

        exit_code = main(["ingest", "shopify-orders"])

    assert exit_code == 0
    run_job.assert_called_once_with(settings=settings)

    captured = capsys.readouterr()
    assert "Loaded 4 rows into shopify_orders with status success." in captured.out


def test_cli_runs_configuration_health_check(capsys) -> None:
    """The CLI runs the configuration health check."""
    result = HealthCheckResult(
        name="config",
        status=HealthStatus.PASS,
        message="Configuration is valid.",
    )

    with (
        patch("alpha60.cli.load_settings") as load_settings,
        patch("alpha60.cli.check_configuration") as check_configuration,
    ):
        settings = object()
        load_settings.return_value = settings
        check_configuration.return_value = result

        exit_code = main(["test", "config"])

    assert exit_code == 0
    check_configuration.assert_called_once_with(settings=settings)

    captured = capsys.readouterr()
    assert "config: pass - Configuration is valid." in captured.out


def test_cli_runs_shopify_health_check(capsys) -> None:
    """The CLI runs the Shopify health check."""
    result = HealthCheckResult(
        name="shopify",
        status=HealthStatus.PASS,
        message="Shopify connection succeeded.",
    )

    with (
        patch("alpha60.cli.load_settings") as load_settings,
        patch("alpha60.cli.check_shopify") as check_shopify,
    ):
        settings = object()
        load_settings.return_value = settings
        check_shopify.return_value = result

        exit_code = main(["test", "shopify"])

    assert exit_code == 0
    check_shopify.assert_called_once_with(settings=settings)

    captured = capsys.readouterr()
    assert "shopify: pass - Shopify connection succeeded." in captured.out


def test_cli_runs_bigquery_health_check(capsys) -> None:
    """The CLI runs the BigQuery health check."""
    result = HealthCheckResult(
        name="bigquery",
        status=HealthStatus.PASS,
        message="BigQuery connection succeeded.",
    )

    with (
        patch("alpha60.cli.load_settings") as load_settings,
        patch("alpha60.cli.check_bigquery") as check_bigquery,
    ):
        settings = object()
        load_settings.return_value = settings
        check_bigquery.return_value = result

        exit_code = main(["test", "bigquery"])

    assert exit_code == 0
    check_bigquery.assert_called_once_with(settings=settings)

    captured = capsys.readouterr()
    assert "bigquery: pass - BigQuery connection succeeded." in captured.out


def test_cli_runs_all_health_checks(capsys) -> None:
    """The CLI runs every health check."""
    result = HealthCheckResult(
        name="test",
        status=HealthStatus.PASS,
        message="OK",
    )

    with (
        patch("alpha60.cli.load_settings") as load_settings,
        patch("alpha60.cli.check_configuration") as check_configuration,
        patch("alpha60.cli.check_shopify") as check_shopify,
        patch("alpha60.cli.check_bigquery") as check_bigquery,
    ):
        settings = object()
        load_settings.return_value = settings

        check_configuration.return_value = result
        check_shopify.return_value = result
        check_bigquery.return_value = result

        exit_code = main(["test", "all"])

    assert exit_code == 0

    check_configuration.assert_called_once_with(settings=settings)
    check_shopify.assert_called_once_with(settings=settings)
    check_bigquery.assert_called_once_with(settings=settings)

    captured = capsys.readouterr()

    assert captured.out.count("test: pass - OK") == 3
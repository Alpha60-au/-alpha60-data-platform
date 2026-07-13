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
    run_job.assert_called_once_with(settings=settings, max_pages=None)

    captured = capsys.readouterr()
    assert "Loaded 4 rows into shopify_orders with status success." in captured.out


def test_cli_passes_shopify_orders_max_pages(capsys) -> None:
    """The CLI passes max_pages to the Shopify orders ingestion job."""
    load_result = WarehouseLoadResult(
        table_id="shopify_orders",
        status=WarehouseLoadStatus.SUCCESS,
        rows_loaded=500,
    )

    with (
        patch("alpha60.cli.load_settings") as load_settings,
        patch("alpha60.cli.run_shopify_orders_ingestion") as run_job,
    ):
        settings = object()
        load_settings.return_value = settings
        run_job.return_value = load_result

        exit_code = main(["ingest", "shopify-orders", "--max-pages", "2"])

    assert exit_code == 0
    run_job.assert_called_once_with(settings=settings, max_pages=2)

    captured = capsys.readouterr()
    assert "Loaded 500 rows into shopify_orders with status success." in captured.out


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


def test_cli_runs_shopify_orders_staging_transformation(capsys) -> None:
    """The CLI runs the Shopify orders staging transformation."""
    from alpha60.transformations.result import (
        TransformationResult,
        TransformationStatus,
    )

    transformation_result = TransformationResult(
        target_table_id="alpha60-data-platform.stg.shopify_orders",
        status=TransformationStatus.SUCCESS,
    )

    with (
        patch("alpha60.cli.load_settings") as load_settings,
        patch(
            "alpha60.cli.run_shopify_orders_staging_transformation"
        ) as run_transformation,
    ):
        settings = object()
        load_settings.return_value = settings
        run_transformation.return_value = transformation_result

        exit_code = main(["transform", "shopify-orders"])

    assert exit_code == 0
    run_transformation.assert_called_once_with(
        settings=settings,
        staging_dataset_id=None,
    )

    captured = capsys.readouterr()
    assert (
        "Transformed alpha60-data-platform.stg.shopify_orders "
        "with status success."
    ) in captured.out


def test_cli_passes_shopify_orders_staging_dataset(capsys) -> None:
    """The CLI passes the staging dataset to the transformation runner."""
    from alpha60.transformations.result import (
        TransformationResult,
        TransformationStatus,
    )

    transformation_result = TransformationResult(
        target_table_id="alpha60-data-platform.alpha60_dev_staging.shopify_orders",
        status=TransformationStatus.SUCCESS,
    )

    with (
        patch("alpha60.cli.load_settings") as load_settings,
        patch(
            "alpha60.cli.run_shopify_orders_staging_transformation"
        ) as run_transformation,
    ):
        settings = object()
        load_settings.return_value = settings
        run_transformation.return_value = transformation_result

        exit_code = main(
            [
                "transform",
                "shopify-orders",
                "--staging-dataset",
                "alpha60_dev_staging",
            ]
        )

    assert exit_code == 0
    run_transformation.assert_called_once_with(
        settings=settings,
        staging_dataset_id="alpha60_dev_staging",
    )


def test_cli_returns_failure_for_failed_transformation(capsys) -> None:
    """The CLI returns a non-zero exit code for failed transformations."""
    from alpha60.transformations.result import (
        TransformationResult,
        TransformationStatus,
    )

    transformation_result = TransformationResult(
        target_table_id="alpha60-data-platform.stg.shopify_orders",
        status=TransformationStatus.FAILED,
        error_message="query failed",
    )

    with (
        patch("alpha60.cli.load_settings") as load_settings,
        patch(
            "alpha60.cli.run_shopify_orders_staging_transformation"
        ) as run_transformation,
    ):
        settings = object()
        load_settings.return_value = settings
        run_transformation.return_value = transformation_result

        exit_code = main(["transform", "shopify-orders"])

    assert exit_code == 1


def test_cli_runs_shopify_order_lines_staging_transformation(capsys) -> None:
    """The CLI runs the Shopify order lines staging transformation."""
    from alpha60.transformations.result import (
        TransformationResult,
        TransformationStatus,
    )

    transformation_result = TransformationResult(
        target_table_id="alpha60-data-platform.stg.shopify_order_lines",
        status=TransformationStatus.SUCCESS,
    )

    with (
        patch("alpha60.cli.load_settings") as load_settings,
        patch(
            "alpha60.cli.run_shopify_order_lines_staging_transformation"
        ) as run_transformation,
    ):
        settings = object()
        load_settings.return_value = settings
        run_transformation.return_value = transformation_result

        exit_code = main(["transform", "shopify-order-lines"])

    assert exit_code == 0
    run_transformation.assert_called_once_with(
        settings=settings,
        staging_dataset_id=None,
    )

    captured = capsys.readouterr()
    assert (
        "Transformed alpha60-data-platform.stg.shopify_order_lines "
        "with status success."
    ) in captured.out


def test_cli_passes_shopify_order_lines_staging_dataset(capsys) -> None:
    """The CLI passes a custom staging dataset for Shopify order lines."""
    from alpha60.transformations.result import (
        TransformationResult,
        TransformationStatus,
    )

    transformation_result = TransformationResult(
        target_table_id="alpha60-data-platform.custom_stg.shopify_order_lines",
        status=TransformationStatus.SUCCESS,
    )

    with (
        patch("alpha60.cli.load_settings") as load_settings,
        patch(
            "alpha60.cli.run_shopify_order_lines_staging_transformation"
        ) as run_transformation,
    ):
        settings = object()
        load_settings.return_value = settings
        run_transformation.return_value = transformation_result

        exit_code = main(
            [
                "transform",
                "shopify-order-lines",
                "--staging-dataset",
                "custom_stg",
            ]
        )

    assert exit_code == 0
    run_transformation.assert_called_once_with(
        settings=settings,
        staging_dataset_id="custom_stg",
    )


def test_cli_runs_shopify_products_staging_transformation(capsys) -> None:
    """The CLI runs the Shopify products staging transformation."""
    from alpha60.transformations.result import (
        TransformationResult,
        TransformationStatus,
    )

    transformation_result = TransformationResult(
        target_table_id="alpha60-data-platform.stg.shopify_products",
        status=TransformationStatus.SUCCESS,
    )

    with (
        patch("alpha60.cli.load_settings") as load_settings,
        patch(
            "alpha60.cli.run_shopify_products_staging_transformation"
        ) as run_transformation,
    ):
        settings = object()
        load_settings.return_value = settings
        run_transformation.return_value = transformation_result

        exit_code = main(["transform", "shopify-products"])

    assert exit_code == 0
    run_transformation.assert_called_once_with(
        settings=settings,
        staging_dataset_id=None,
    )

    captured = capsys.readouterr()
    assert (
        "Transformed alpha60-data-platform.stg.shopify_products "
        "with status success."
    ) in captured.out


def test_cli_passes_shopify_products_staging_dataset(capsys) -> None:
    """The CLI passes a custom staging dataset for Shopify products."""
    from alpha60.transformations.result import (
        TransformationResult,
        TransformationStatus,
    )

    transformation_result = TransformationResult(
        target_table_id="alpha60-data-platform.custom_stg.shopify_products",
        status=TransformationStatus.SUCCESS,
    )

    with (
        patch("alpha60.cli.load_settings") as load_settings,
        patch(
            "alpha60.cli.run_shopify_products_staging_transformation"
        ) as run_transformation,
    ):
        settings = object()
        load_settings.return_value = settings
        run_transformation.return_value = transformation_result

        exit_code = main(
            [
                "transform",
                "shopify-products",
                "--staging-dataset",
                "custom_stg",
            ]
        )

    assert exit_code == 0
    run_transformation.assert_called_once_with(
        settings=settings,
        staging_dataset_id="custom_stg",
    )


def test_cli_runs_daily_refresh(capsys) -> None:
    """The CLI runs the daily refresh workflow."""
    from alpha60.pipelines.daily_refresh import (
        DailyRefreshResult,
        DailyRefreshStatus,
    )

    products_result = WarehouseLoadResult(
        table_id="shopify_products",
        status=WarehouseLoadStatus.SUCCESS,
        rows_loaded=3,
    )
    orders_result = WarehouseLoadResult(
        table_id="shopify_orders",
        status=WarehouseLoadStatus.SUCCESS,
        rows_loaded=4,
    )
    inventory_result = WarehouseLoadResult(
        table_id="shopify_inventory_levels",
        status=WarehouseLoadStatus.SUCCESS,
        rows_loaded=5,
    )
    refresh_result = DailyRefreshResult(
        status=DailyRefreshStatus.SUCCESS,
        products_result=products_result,
        orders_result=orders_result,
        inventory_levels_result=inventory_result,
    )

    with (
        patch("alpha60.cli.load_settings") as load_settings,
        patch("alpha60.cli.run_daily_refresh") as run_refresh,
    ):
        settings = object()
        load_settings.return_value = settings
        run_refresh.return_value = refresh_result

        exit_code = main(["refresh", "daily"])

    assert exit_code == 0
    run_refresh.assert_called_once_with(
        settings=settings,
        orders_max_pages=None,
    )

    captured = capsys.readouterr()
    assert (
        "Daily refresh completed successfully: "
        "products=3, orders=4, inventory_levels=5."
    ) in captured.out


def test_cli_passes_daily_refresh_orders_max_pages() -> None:
    """The CLI passes an optional order page limit to the daily refresh."""
    from alpha60.pipelines.daily_refresh import (
        DailyRefreshResult,
        DailyRefreshStatus,
    )

    refresh_result = DailyRefreshResult(
        status=DailyRefreshStatus.SUCCESS,
    )

    with (
        patch("alpha60.cli.load_settings") as load_settings,
        patch("alpha60.cli.run_daily_refresh") as run_refresh,
    ):
        settings = object()
        load_settings.return_value = settings
        run_refresh.return_value = refresh_result

        exit_code = main(
            [
                "refresh",
                "daily",
                "--orders-max-pages",
                "2",
            ]
        )

    assert exit_code == 0
    run_refresh.assert_called_once_with(
        settings=settings,
        orders_max_pages=2,
    )


def test_cli_returns_failure_for_failed_daily_refresh(capsys) -> None:
    """The CLI returns a non-zero exit code when the daily refresh fails."""
    from alpha60.pipelines.daily_refresh import (
        DailyRefreshResult,
        DailyRefreshStatus,
    )

    refresh_result = DailyRefreshResult(
        status=DailyRefreshStatus.FAILED,
        failed_stage="shopify-orders",
        error_message="Orders load failed",
    )

    with (
        patch("alpha60.cli.load_settings") as load_settings,
        patch("alpha60.cli.run_daily_refresh") as run_refresh,
    ):
        settings = object()
        load_settings.return_value = settings
        run_refresh.return_value = refresh_result

        exit_code = main(["refresh", "daily"])

    assert exit_code == 1

    captured = capsys.readouterr()
    assert (
        "Daily refresh failed at shopify-orders: Orders load failed"
        in captured.out
    )

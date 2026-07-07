"""Tests for Shopify order staging transformation."""

from unittest.mock import Mock

from alpha60.transformations.result import TransformationStatus
from alpha60.transformations.shopify_orders import ShopifyOrdersStagingTransformation
from alpha60.warehouse.bigquery.config import BigQueryConfig


def test_shopify_orders_staging_transformation_runs_rendered_sql() -> None:
    """The transformation renders and executes the staging SQL."""
    client = Mock()

    transformation = ShopifyOrdersStagingTransformation(
        client=client,
        project_id="alpha60-data-platform",
        raw_dataset_id="raw",
        staging_dataset_id="stg",
    )

    result = transformation.run()

    assert result.status == TransformationStatus.SUCCESS
    assert result.target_table_id == "alpha60-data-platform.stg.shopify_orders"

    client.query.assert_called_once()
    sql = client.query.call_args.args[0]

    assert "CREATE OR REPLACE TABLE `alpha60-data-platform.stg.shopify_orders`" in sql
    assert "FROM `alpha60-data-platform.raw.shopify_orders`" in sql
    assert "SAFE_CAST(record_id AS INT64) AS order_id" in sql
    assert "payload" in sql


def test_shopify_orders_staging_transformation_can_be_created_from_config() -> None:
    """The transformation can be created from raw BigQuery config."""
    client = Mock()
    config = BigQueryConfig(
        project_id="alpha60-data-platform",
        dataset_id="raw",
        location="australia-southeast1",
    )

    transformation = ShopifyOrdersStagingTransformation.from_config(
        client=client,
        raw_config=config,
        staging_dataset_id="stg",
    )

    result = transformation.run()

    assert result.status == TransformationStatus.SUCCESS
    assert result.target_table_id == "alpha60-data-platform.stg.shopify_orders"

    sql = client.query.call_args.args[0]
    assert "`alpha60-data-platform.raw.shopify_orders`" in sql
    assert "`alpha60-data-platform.stg.shopify_orders`" in sql


def test_shopify_orders_staging_transformation_returns_failed_result() -> None:
    """Query errors are returned as failed transformation results."""
    client = Mock()
    client.query.side_effect = RuntimeError("BigQuery query failed")

    transformation = ShopifyOrdersStagingTransformation(
        client=client,
        project_id="alpha60-data-platform",
        raw_dataset_id="raw",
        staging_dataset_id="stg",
    )

    result = transformation.run()

    assert result.status == TransformationStatus.FAILED
    assert result.target_table_id == "alpha60-data-platform.stg.shopify_orders"
    assert result.error_message == "BigQuery query failed"

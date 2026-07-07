"""Tests for transformation pipeline orchestration."""

from unittest.mock import Mock

from alpha60.config.bigquery import BigQuerySettings
from alpha60.config.settings import Settings
from alpha60.config.shopify import ShopifySettings
from alpha60.transformations.pipeline import (
    TransformationPipeline,
    TransformationPipelineStep,
)
from alpha60.transformations.result import TransformationResult, TransformationStatus


def _settings() -> Settings:
    """Create test settings."""
    return Settings(
        environment="test",
        log_level="INFO",
        shopify=ShopifySettings(shop_domain="alpha60.myshopify.com"),
        bigquery=BigQuerySettings(
            project_id="alpha60-data-platform",
            dataset_id="raw",
            staging_dataset_id="stg",
        ),
    )


def test_transformation_pipeline_runs_steps_in_order() -> None:
    """The pipeline runs every step in dependency order."""
    settings = _settings()

    first = Mock(
        return_value=TransformationResult(
            target_table_id="project.stg.first",
            status=TransformationStatus.SUCCESS,
        )
    )
    second = Mock(
        return_value=TransformationResult(
            target_table_id="project.stg.second",
            status=TransformationStatus.SUCCESS,
        )
    )

    pipeline = TransformationPipeline(
        steps=[
            TransformationPipelineStep(name="first", run=first),
            TransformationPipelineStep(name="second", run=second),
        ]
    )

    result = pipeline.run(settings=settings, staging_dataset_id="stg")

    assert result.status == TransformationStatus.SUCCESS
    assert len(result.results) == 2

    first.assert_called_once_with(settings=settings, staging_dataset_id="stg")
    second.assert_called_once_with(settings=settings, staging_dataset_id="stg")


def test_transformation_pipeline_stops_after_failure() -> None:
    """The pipeline stops running when a step fails."""
    settings = _settings()

    first = Mock(
        return_value=TransformationResult(
            target_table_id="project.stg.first",
            status=TransformationStatus.FAILED,
            error_message="query failed",
        )
    )
    second = Mock()

    pipeline = TransformationPipeline(
        steps=[
            TransformationPipelineStep(name="first", run=first),
            TransformationPipelineStep(name="second", run=second),
        ]
    )

    result = pipeline.run(settings=settings)

    assert result.status == TransformationStatus.FAILED
    assert len(result.results) == 1

    first.assert_called_once_with(settings=settings, staging_dataset_id="stg")
    second.assert_not_called()

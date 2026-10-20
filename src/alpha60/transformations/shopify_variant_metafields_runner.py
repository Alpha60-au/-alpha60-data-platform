"""Composition root for Shopify variant metafield staging."""

from alpha60.config.settings import Settings
from alpha60.transformations.result import TransformationResult
from alpha60.transformations.shopify_variant_metafields import (
    create_shopify_variant_metafields_staging_transformation,
)
from alpha60.warehouse.bigquery.config import BigQueryConfig
from alpha60.warehouse.bigquery.factory import create_bigquery_client


def run_shopify_variant_metafields_staging_transformation(
    settings: Settings,
    staging_dataset_id: str | None = None,
) -> TransformationResult:
    """Run the Shopify variant metafield staging transformation."""
    raw_config = BigQueryConfig(
        project_id=settings.bigquery.project_id,
        dataset_id=settings.bigquery.dataset_id,
        location=settings.bigquery.location,
    )

    client = create_bigquery_client(config=raw_config)
    transformation = (
        create_shopify_variant_metafields_staging_transformation(
            client=client,
            raw_config=raw_config,
            staging_dataset_id=(
                staging_dataset_id
                or settings.bigquery.staging_dataset_id
            ),
        )
    )

    return transformation.run()

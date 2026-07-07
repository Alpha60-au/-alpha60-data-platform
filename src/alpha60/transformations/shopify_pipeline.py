"""Shopify transformation pipeline."""

from alpha60.transformations.pipeline import (
    TransformationPipeline,
    TransformationPipelineStep,
)
from alpha60.transformations.shopify_order_lines_runner import (
    run_shopify_order_lines_staging_transformation,
)
from alpha60.transformations.shopify_orders_runner import (
    run_shopify_orders_staging_transformation,
)
from alpha60.transformations.shopify_product_variants_runner import (
    run_shopify_product_variants_staging_transformation,
)
from alpha60.transformations.shopify_products_runner import (
    run_shopify_products_staging_transformation,
)


def create_shopify_transformation_pipeline() -> TransformationPipeline:
    """Create the Shopify transformation pipeline in dependency order."""
    return TransformationPipeline(
        steps=[
            TransformationPipelineStep(
                name="shopify-orders",
                run=run_shopify_orders_staging_transformation,
            ),
            TransformationPipelineStep(
                name="shopify-order-lines",
                run=run_shopify_order_lines_staging_transformation,
            ),
            TransformationPipelineStep(
                name="shopify-products",
                run=run_shopify_products_staging_transformation,
            ),
            TransformationPipelineStep(
                name="shopify-product-variants",
                run=run_shopify_product_variants_staging_transformation,
            ),
        ]
    )

"""Shopify variant metafield ingestion job."""

from typing import Protocol

from alpha60.core.models.record import Record
from alpha60.jobs.result import IngestionJobResult
from alpha60.warehouse.loader import WarehouseLoader


_DEFAULT_VARIANT_METAFIELDS_TABLE_ID = "shopify_variant_metafields"


class ShopifyVariantMetafieldsClient(Protocol):
    """Client capable of returning Shopify variant metafield records."""

    def get_variant_metafield_records(self) -> list[Record]:
        """Fetch desired-stock metafields for Shopify variants."""


def load_shopify_variant_metafields(
    shopify_client: ShopifyVariantMetafieldsClient,
    warehouse_loader: WarehouseLoader,
    table_id: str = _DEFAULT_VARIANT_METAFIELDS_TABLE_ID,
) -> IngestionJobResult:
    """Load Shopify variant metafield records into the warehouse."""
    records = shopify_client.get_variant_metafield_records()

    warehouse_result = warehouse_loader.load(
        table_id=table_id,
        records=records,
    )

    return IngestionJobResult(
        warehouse_result=warehouse_result,
        records_processed=len(records),
        latest_cursor=None,
    )

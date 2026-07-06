"""Shopify product ingestion jobs."""

from datetime import datetime
from typing import Protocol

from alpha60.core.models.record import Record
from alpha60.warehouse.loader import WarehouseLoader
from alpha60.warehouse.types import WarehouseLoadResult


_DEFAULT_PRODUCTS_TABLE_ID = "shopify_products"


class ShopifyProductsClient(Protocol):
    """Client capable of returning Shopify product records."""

    def get_product_records(
        self,
        updated_since: datetime | None = None,
    ) -> list[Record]:
        """Fetch Shopify products as platform records."""


def load_shopify_products(
    shopify_client: ShopifyProductsClient,
    warehouse_loader: WarehouseLoader,
    table_id: str = _DEFAULT_PRODUCTS_TABLE_ID,
    updated_since: datetime | None = None,
) -> WarehouseLoadResult:
    """Load Shopify product records into a warehouse table."""
    records = shopify_client.get_product_records(updated_since=updated_since)

    return warehouse_loader.load(
        table_id=table_id,
        records=records,
    )
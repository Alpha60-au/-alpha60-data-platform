"""Tests for Shopify product ingestion jobs."""

from collections.abc import Iterable
from datetime import UTC, datetime

from alpha60.core.models.record import Record
from alpha60.jobs.shopify_products import load_shopify_products
from alpha60.warehouse.types import WarehouseLoadResult, WarehouseLoadStatus


class FakeShopifyClient:
    """Fake Shopify client for job tests."""

    def __init__(self) -> None:
        """Create a fake Shopify client."""
        self.updated_since: datetime | None = None

    def get_product_records(
        self,
        updated_since: datetime | None = None,
    ) -> list[Record]:
        """Return fake product records."""
        self.updated_since = updated_since

        return [
            Record(
                source="shopify",
                entity="product",
                record_id="123",
                extracted_at=datetime(2026, 7, 3, 12, 30, tzinfo=UTC),
                payload={"title": "Black Jacket"},
            )
        ]


class FakeWarehouseLoader:
    """Fake warehouse loader for job tests."""

    def __init__(self) -> None:
        """Create a fake warehouse loader."""
        self.table_id: str | None = None
        self.records: list[Record] = []

    def load(
        self,
        table_id: str,
        records: Iterable[Record],
    ) -> WarehouseLoadResult:
        """Record load inputs and return a successful result."""
        self.table_id = table_id
        self.records = list(records)

        return WarehouseLoadResult(
            table_id=table_id,
            status=WarehouseLoadStatus.SUCCESS,
            rows_loaded=len(self.records),
        )


def test_load_shopify_products_loads_records_to_default_table() -> None:
    """Shopify product records are loaded into the default warehouse table."""
    shopify_client = FakeShopifyClient()
    warehouse_loader = FakeWarehouseLoader()

    result = load_shopify_products(
        shopify_client=shopify_client,
        warehouse_loader=warehouse_loader,
    )

    assert result.status == WarehouseLoadStatus.SUCCESS
    assert result.table_id == "shopify_products"
    assert result.rows_loaded == 1

    assert shopify_client.updated_since is None
    assert warehouse_loader.table_id == "shopify_products"
    assert warehouse_loader.records[0].record_id == "123"


def test_load_shopify_products_allows_custom_table_id() -> None:
    """Shopify product records can be loaded into a custom table."""
    warehouse_loader = FakeWarehouseLoader()

    result = load_shopify_products(
        shopify_client=FakeShopifyClient(),
        warehouse_loader=warehouse_loader,
        table_id="raw_shopify_products",
    )

    assert result.table_id == "raw_shopify_products"
    assert warehouse_loader.table_id == "raw_shopify_products"


def test_load_shopify_products_passes_updated_since_to_client() -> None:
    """Shopify products can be filtered by updated timestamp."""
    updated_since = datetime(2026, 7, 3, 12, 30, tzinfo=UTC)
    shopify_client = FakeShopifyClient()
    warehouse_loader = FakeWarehouseLoader()

    result = load_shopify_products(
        shopify_client=shopify_client,
        warehouse_loader=warehouse_loader,
        updated_since=updated_since,
    )

    assert result.status == WarehouseLoadStatus.SUCCESS
    assert shopify_client.updated_since == updated_since
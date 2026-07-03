"""Tests for the BigQuery warehouse loader."""

from collections.abc import Iterable
from datetime import UTC, datetime
from typing import Any

from alpha60.core.models.record import Record
from alpha60.warehouse.bigquery.config import BigQueryConfig
from alpha60.warehouse.bigquery.loader import BigQueryLoader
from alpha60.warehouse.types import WarehouseLoadStatus


class FakeBigQueryClient:
    """Fake BigQuery client for loader tests."""

    def __init__(self, rows_loaded: int = 0) -> None:
        """Create a fake BigQuery client."""
        self.rows_loaded = rows_loaded
        self.table_id: str | None = None
        self.rows: list[dict[str, Any]] = []

    def insert_rows(
        self,
        table_id: str,
        rows: Iterable[dict[str, Any]],
    ) -> int:
        """Record inserted rows and return configured row count."""
        self.table_id = table_id
        self.rows = list(rows)
        return self.rows_loaded


class FailingBigQueryClient:
    """Fake BigQuery client that raises an error."""

    def insert_rows(
        self,
        table_id: str,
        rows: Iterable[dict[str, Any]],
    ) -> int:
        """Raise a fake BigQuery loading error."""
        raise RuntimeError("BigQuery insert failed")


def test_bigquery_loader_loads_records() -> None:
    """The BigQuery loader converts records and inserts them through the client."""
    client = FakeBigQueryClient(rows_loaded=1)
    loader = BigQueryLoader(
        config=BigQueryConfig(
            project_id="alpha60-dev",
            dataset_id="raw",
        ),
        client=client,
    )
    record = Record(
        source="shopify",
        entity="products",
        record_id="123",
        extracted_at=datetime(2026, 7, 3, 12, 30, tzinfo=UTC),
        payload={"title": "Black Jacket"},
    )

    result = loader.load(table_id="shopify_products", records=[record])

    assert result.status == WarehouseLoadStatus.SUCCESS
    assert result.table_id == "alpha60-dev.raw.shopify_products"
    assert result.rows_loaded == 1
    assert result.error_message is None

    assert client.table_id == "alpha60-dev.raw.shopify_products"
    assert client.rows == [
        {
            "source": "shopify",
            "entity": "products",
            "record_id": "123",
            "extracted_at": "2026-07-03T12:30:00+00:00",
            "payload": {"title": "Black Jacket"},
        }
    ]


def test_bigquery_loader_returns_failed_result_when_client_fails() -> None:
    """The BigQuery loader returns a failed result when the client raises."""
    loader = BigQueryLoader(
        config=BigQueryConfig(
            project_id="alpha60-dev",
            dataset_id="raw",
        ),
        client=FailingBigQueryClient(),
    )
    record = Record(
        source="shopify",
        entity="products",
        record_id="123",
        extracted_at=datetime(2026, 7, 3, 12, 30, tzinfo=UTC),
        payload={"title": "Black Jacket"},
    )

    result = loader.load(table_id="shopify_products", records=[record])

    assert result.status == WarehouseLoadStatus.FAILED
    assert result.table_id == "alpha60-dev.raw.shopify_products"
    assert result.rows_loaded == 0
    assert result.error_message == "BigQuery insert failed"
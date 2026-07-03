"""Unit tests for the BigQuery incremental state repository."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from datetime import UTC, datetime
from typing import Any

from alpha60.warehouse.bigquery.state_repository import BigQueryStateRepository


class FakeBigQueryClient:
    """Fake BigQuery client for state repository tests."""

    def __init__(self, query_rows: list[dict[str, Any]]) -> None:
        """Create a fake BigQuery client."""
        self.query_rows = query_rows
        self.sql: str | None = None
        self.parameters: Sequence[Any] | None = None

    def load_rows(
        self,
        table_id: str,
        rows: Iterable[dict[str, Any]],
    ) -> int:
        """Return no loaded rows."""
        return 0

    def query(
        self,
        sql: str,
        parameters: Sequence[Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Record query details and return configured rows."""
        self.sql = sql
        self.parameters = parameters
        return self.query_rows


def test_bigquery_state_repository_get_state_returns_none_when_not_found() -> None:
    """get_state returns None when no state row exists for a job."""
    client = FakeBigQueryClient(query_rows=[])
    repository = BigQueryStateRepository(
        table_id="alpha60-dev.warehouse.platform_state",
        client=client,
    )

    state = repository.get_state("shopify-products")

    assert state is None
    assert "FROM `alpha60-dev.warehouse.platform_state`" in str(client.sql)
    assert client.parameters is not None


def test_bigquery_state_repository_get_state_returns_incremental_state() -> None:
    """get_state returns IncrementalState when a matching row exists."""
    cursor_value = datetime(2026, 7, 3, 12, 30, tzinfo=UTC)
    client = FakeBigQueryClient(
        query_rows=[
            {
                "job_name": "shopify-products",
                "cursor_field": "updated_at",
                "cursor_value": cursor_value,
            }
        ],
    )
    repository = BigQueryStateRepository(
        table_id="alpha60-dev.warehouse.platform_state",
        client=client,
    )

    state = repository.get_state("shopify-products")

    assert state is not None
    assert state.job_name == "shopify-products"
    assert state.cursor_field == "updated_at"
    assert state.cursor_value == cursor_value


def test_bigquery_state_repository_rejects_invalid_cursor_value() -> None:
    """get_state rejects cursor values that are not datetime values."""
    client = FakeBigQueryClient(
        query_rows=[
            {
                "job_name": "shopify-products",
                "cursor_field": "updated_at",
                "cursor_value": "2026-07-03T12:30:00Z",
            }
        ],
    )
    repository = BigQueryStateRepository(
        table_id="alpha60-dev.warehouse.platform_state",
        client=client,
    )

    try:
        repository.get_state("shopify-products")
    except TypeError as exc:
        assert "cursor_value must be a datetime or None" in str(exc)
    else:
        raise AssertionError("Expected TypeError")
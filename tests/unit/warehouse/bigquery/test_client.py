"""Tests for the BigQuery client protocol."""

from typing import assert_type

from alpha60.warehouse.bigquery.client import BigQueryClient


def test_bigquery_client_protocol_is_importable() -> None:
    """The BigQuery client protocol can be used for typing."""
    # This test exists to ensure the protocol is importable and
    # participates in static type checking.
    assert_type(BigQueryClient, type[BigQueryClient])
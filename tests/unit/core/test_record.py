# tests/test_record.py

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime

import pytest

from alpha60.core.models.record import Record


def test_record_stores_fields() -> None:
    extracted_at = datetime.now(UTC)

    record = Record(
        source="shopify",
        entity="product",
        record_id="123",
        extracted_at=extracted_at,
        payload={"title": "Test Product"},
    )

    assert record.source == "shopify"
    assert record.entity == "product"
    assert record.record_id == "123"
    assert record.extracted_at == extracted_at
    assert record.payload == {"title": "Test Product"}


def test_record_is_immutable() -> None:
    record = Record(
        source="shopify",
        entity="product",
        record_id="123",
        extracted_at=datetime.now(UTC),
        payload={},
    )

    with pytest.raises(FrozenInstanceError):
        record.source = "cin7"  # type: ignore[misc]
"""Shopify inventory level resource."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Protocol

import httpx

from alpha60.core.models.record import Record


class ShopifyRequestClient(Protocol):
    """Protocol for Shopify request clients."""

    def get(
        self,
        path: str,
        *,
        params: dict[str, str] | None = None,
    ) -> httpx.Response:
        """Perform a Shopify GET request."""


def _chunked(values: list[int], size: int) -> list[list[int]]:
    """Split values into fixed-size chunks."""
    return [values[index : index + size] for index in range(0, len(values), size)]


class InventoryLevelsResource:
    """Access Shopify inventory level resources."""

    def __init__(self, client: ShopifyRequestClient) -> None:
        """Initialize the resource."""
        self._client = client

    def get_inventory_levels(
        self,
        inventory_item_ids: list[int],
    ) -> list[dict[str, object]]:
        """Fetch inventory levels from Shopify."""
        records: list[dict[str, object]] = []

        for inventory_item_id_chunk in _chunked(inventory_item_ids, 50):
            params: dict[str, str] | None = {
                "inventory_item_ids": ",".join(
                    str(inventory_item_id)
                    for inventory_item_id in inventory_item_id_chunk
                ),
                "limit": "250",
            }

            while params is not None:
                response = self._client.get(
                    "/inventory_levels.json",
                    params=params,
                )
                data = response.json()

                inventory_levels = data.get("inventory_levels", [])
                if isinstance(inventory_levels, list):
                    records.extend(
                        inventory_level
                        for inventory_level in inventory_levels
                        if isinstance(inventory_level, dict)
                    )

                next_link = response.links.get("next", {})
                next_url = next_link.get("url")

                if not next_url:
                    params = None
                    continue

                next_request = httpx.URL(next_url)
                page_info = next_request.params.get("page_info")

                if page_info is None:
                    params = None
                else:
                    params = {
                        "page_info": page_info,
                        "limit": "250",
                    }

        return records

    def get_inventory_level_records(
        self,
        inventory_item_ids: list[int],
    ) -> list[Record]:
        """Fetch Shopify inventory levels as platform records."""
        extracted_at = datetime.now(UTC)

        return [
            Record(
                source="shopify",
                entity="inventory_level",
                record_id=(
                    f"{inventory_level['inventory_item_id']}-"
                    f"{inventory_level['location_id']}"
                ),
                extracted_at=extracted_at,
                payload=inventory_level,
            )
            for inventory_level in self.get_inventory_levels(
                inventory_item_ids=inventory_item_ids,
            )
            if "inventory_item_id" in inventory_level
            and "location_id" in inventory_level
        ]

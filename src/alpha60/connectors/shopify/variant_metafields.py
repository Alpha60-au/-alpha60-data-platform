"""Shopify variant desired-stock metafield resource."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Protocol

import httpx

from alpha60.core.models.record import Record


class ShopifyRequestClient(Protocol):
    """Protocol for Shopify GraphQL requests."""

    def post(
        self,
        path: str,
        *,
        json: dict[str, object] | None = None,
    ) -> httpx.Response:
        """Perform a Shopify POST request."""


_QUERY = """
query VariantDesiredStockLevels($cursor: String) {
  productVariants(first: 250, after: $cursor) {
    nodes {
      legacyResourceId
      metafields(first: 100, namespace: "custom") {
        nodes {
          namespace
          key
          value
          type
          updatedAt
        }
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
"""


class VariantMetafieldsResource:
    """Access desired-stock metafields for Shopify variants."""

    def __init__(self, client: ShopifyRequestClient) -> None:
        """Initialize the resource."""
        self._client = client

    def get_variant_metafield_records(self) -> list[Record]:
        """Fetch the configured desired-stock metafields for every variant."""
        extracted_at = datetime.now(UTC)
        cursor: str | None = None
        records: list[Record] = []

        while True:
            response = self._client.post(
                "/graphql.json",
                json={
                    "query": _QUERY,
                    "variables": {"cursor": cursor},
                },
            )
            response_data = response.json()

            errors = response_data.get("errors")
            if errors:
                raise RuntimeError(f"Shopify GraphQL request failed: {errors}")

            data = response_data.get("data", {})
            variants = data.get("productVariants", {})
            nodes = variants.get("nodes", [])

            if isinstance(nodes, list):
                for node in nodes:
                    if not isinstance(node, dict):
                        continue

                    variant_id = node.get("legacyResourceId")
                    if variant_id is None:
                        continue

                    records.append(
                        Record(
                            source="shopify",
                            entity="variant_metafields",
                            record_id=str(variant_id),
                            extracted_at=extracted_at,
                            payload={
                                "variant_id": variant_id,
                                "metafields": [
                                    metafield
                                    for metafield in node.get(
                                        "metafields", {}
                                    ).get("nodes", [])
                                    if metafield.get("key", "").startswith(
                                        "desired_stock_level_"
                                    )
                                ],
                            },
                        )
                    )

            page_info = variants.get("pageInfo", {})
            if not page_info.get("hasNextPage"):
                break

            next_cursor = page_info.get("endCursor")
            if not isinstance(next_cursor, str) or not next_cursor:
                raise RuntimeError(
                    "Shopify GraphQL pagination did not return an end cursor"
                )

            cursor = next_cursor

        return records

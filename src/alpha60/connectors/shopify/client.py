"""Shopify Admin API client."""

from __future__ import annotations

from datetime import datetime

import httpx

from alpha60.core.http.client import HTTPClient
from alpha60.core.models.record import Record

from .customers import CustomersResource
from .locations import LocationsResource
from .inventory_levels import InventoryLevelsResource
from .orders import OrdersResource
from .products import ProductsResource
from .variant_metafields import VariantMetafieldsResource


class ShopifyClient:
    """Client for Shopify Admin API requests."""

    def __init__(
        self,
        shop_domain: str,
        access_token: str,
        api_version: str = "2025-01",
        http_client: HTTPClient | None = None,
    ) -> None:
        """Initialize the Shopify client."""
        self.shop_domain = shop_domain
        self.access_token = access_token
        self.api_version = api_version
        self.http_client = http_client or HTTPClient()
        self.orders = OrdersResource(self)
        self.products = ProductsResource(self)
        self.variant_metafields = VariantMetafieldsResource(self)
        self.customers = CustomersResource(self)
        self.locations = LocationsResource(self)
        self.inventory_levels = InventoryLevelsResource(self)

    def build_url(self, path: str) -> str:
        """Build a Shopify Admin API URL."""
        normalized_path = path if path.startswith("/") else f"/{path}"

        return (
            f"https://{self.shop_domain}"
            f"/admin/api/{self.api_version}"
            f"{normalized_path}"
        )

    def get(
        self,
        path: str,
        *,
        params: dict[str, str] | None = None,
    ) -> httpx.Response:
        """Perform an authenticated Shopify GET request."""
        return self.http_client.get(
            self.build_url(path),
            headers={"X-Shopify-Access-Token": self.access_token},
            params=params,
        )

    def post(
        self,
        path: str,
        *,
        json: dict[str, object] | None = None,
    ) -> httpx.Response:
        """Perform an authenticated Shopify POST request."""
        return self.http_client.post(
            self.build_url(path),
            headers={"X-Shopify-Access-Token": self.access_token},
            json=json,
        )

    def test_connection(self) -> bool:
        """Verify Shopify credentials."""
        response = self.get("/shop.json")
        return response.status_code == 200

    def get_orders(
        self,
        updated_since: datetime | None = None,
        max_pages: int | None = None,
    ) -> list[dict[str, object]]:
        """Fetch orders from Shopify."""
        return self.orders.get_orders(
            updated_since=updated_since,
            max_pages=max_pages,
        )

    def get_order_records(
        self,
        updated_since: datetime | None = None,
        max_pages: int | None = None,
    ) -> list[Record]:
        """Fetch Shopify orders as platform records."""
        return self.orders.get_order_records(
            updated_since=updated_since,
            max_pages=max_pages,
        )

    def get_products(
        self,
        updated_since: datetime | None = None,
    ) -> list[dict[str, object]]:
        """Fetch products from Shopify."""
        return self.products.get_products(updated_since=updated_since)

    def get_product_records(
        self,
        updated_since: datetime | None = None,
    ) -> list[Record]:
        """Fetch Shopify products as platform records."""
        return self.products.get_product_records(updated_since=updated_since)

    def get_variant_metafield_records(self) -> list[Record]:
        """Fetch desired-stock metafields for Shopify variants."""
        return self.variant_metafields.get_variant_metafield_records()

    def get_customers(
        self,
        updated_since: datetime | None = None,
        max_pages: int | None = None,
    ) -> list[dict[str, object]]:
        """Fetch customers from Shopify."""
        return self.customers.get_customers(
            updated_since=updated_since,
            max_pages=max_pages,
        )

    def get_customer_records(
        self,
        updated_since: datetime | None = None,
        max_pages: int | None = None,
    ) -> list[Record]:
        """Fetch Shopify customers as platform records."""
        return self.customers.get_customer_records(
            updated_since=updated_since,
            max_pages=max_pages,
        )

    def get_locations(self) -> list[dict[str, object]]:
        """Fetch locations from Shopify."""
        return self.locations.get_locations()

    def get_location_records(self) -> list[Record]:
        """Fetch Shopify locations as platform records."""
        return self.locations.get_location_records()
    def get_inventory_levels(
        self,
        inventory_item_ids: list[int],
    ) -> list[dict[str, object]]:
        """Fetch inventory levels from Shopify."""
        return self.inventory_levels.get_inventory_levels(
            inventory_item_ids=inventory_item_ids,
        )

    def get_inventory_level_records(
        self,
        inventory_item_ids: list[int],
    ) -> list[Record]:
        """Fetch Shopify inventory levels as platform records."""
        return self.inventory_levels.get_inventory_level_records(
            inventory_item_ids=inventory_item_ids,
        )


"""Tests for the Shopify API client."""

from __future__ import annotations

import httpx

from alpha60.connectors.shopify.client import ShopifyClient
from alpha60.core.http.client import HTTPClient


def test_shopify_client_builds_admin_api_url() -> None:
    client = ShopifyClient(
        shop_domain="alpha60-test.myshopify.com",
        access_token="test-token",
    )

    url = client.build_url("/products.json")

    assert url == "https://alpha60-test.myshopify.com/admin/api/2025-01/products.json"


def test_shopify_client_sends_authenticated_get_request() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert str(request.url) == (
            "https://alpha60-test.myshopify.com/admin/api/2025-01/products.json"
        )
        assert request.headers["X-Shopify-Access-Token"] == "test-token"

        return httpx.Response(status_code=200, json={"products": []})

    http_client = HTTPClient(transport=httpx.MockTransport(handler))

    client = ShopifyClient(
        shop_domain="alpha60-test.myshopify.com",
        access_token="test-token",
        http_client=http_client,
    )

    response = client.get("/products.json")

    assert response.status_code == 200
    assert response.json() == {"products": []}

    http_client.close()
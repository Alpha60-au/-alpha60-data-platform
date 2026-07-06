"""Tests for Shopify authentication."""

from __future__ import annotations

import httpx

from alpha60.connectors.shopify.auth import ShopifyAuthenticator
from alpha60.core.http.client import HTTPClient


def test_shopify_authenticator_exchanges_client_credentials_for_access_token() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert str(request.url) == (
            "https://alpha60-test.myshopify.com/admin/oauth/access_token"
        )
        assert request.headers["Content-Type"] == "application/x-www-form-urlencoded"

        body = request.content.decode()
        assert "grant_type=client_credentials" in body
        assert "client_id=test-client-id" in body
        assert "client_secret=test-client-secret" in body

        return httpx.Response(
            status_code=200,
            json={
                "access_token": "temporary-token",
                "scope": "read_products,read_inventory,read_orders",
                "expires_in": 86399,
            },
        )

    http_client = HTTPClient(transport=httpx.MockTransport(handler))
    authenticator = ShopifyAuthenticator(
        shop_domain="alpha60-test.myshopify.com",
        client_id="test-client-id",
        client_secret="test-client-secret",
        http_client=http_client,
    )

    assert authenticator.get_access_token() == "temporary-token"

    http_client.close()


def test_shopify_authenticator_caches_access_token_for_process_lifetime() -> None:
    request_count = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal request_count
        request_count += 1

        return httpx.Response(
            status_code=200,
            json={
                "access_token": "cached-token",
                "scope": "read_products",
                "expires_in": 86399,
            },
        )

    http_client = HTTPClient(transport=httpx.MockTransport(handler))
    authenticator = ShopifyAuthenticator(
        shop_domain="alpha60-test.myshopify.com",
        client_id="test-client-id",
        client_secret="test-client-secret",
        http_client=http_client,
    )

    assert authenticator.get_access_token() == "cached-token"
    assert authenticator.get_access_token() == "cached-token"
    assert request_count == 1

    http_client.close()
"""Tests for the generic HTTP client."""

from alpha60.core.http.client import HTTPClient
from alpha60.core.http.config import HTTPConfig


def test_http_client_uses_default_configuration() -> None:
    client = HTTPClient()

    assert client.config == HTTPConfig()


def test_http_client_accepts_custom_configuration() -> None:
    config = HTTPConfig(timeout=10.0)

    client = HTTPClient(config=config)

    assert client.config is config
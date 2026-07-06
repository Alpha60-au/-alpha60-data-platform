"""Shopify configuration models."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ShopifySettings:
    """Configuration required to connect to Shopify."""

    shop_domain: str
    access_token: str
    api_version: str = "2025-01"

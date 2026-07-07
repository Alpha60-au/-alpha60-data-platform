"""Runtime settings for the ALPHA60 Data Platform."""

from __future__ import annotations

from dataclasses import dataclass
import os

from alpha60.config.bigquery import BigQuerySettings
from alpha60.config.shopify import ShopifySettings


_DEFAULT_ENVIRONMENT = "development"
_DEFAULT_LOG_LEVEL = "INFO"
_DEFAULT_SHOPIFY_API_VERSION = "2025-01"
_DEFAULT_BIGQUERY_LOCATION = "australia-southeast1"
_DEFAULT_BIGQUERY_STAGING_DATASET_ID = "stg"


@dataclass(frozen=True, slots=True)
class Settings:
    """Application settings loaded from the runtime environment."""

    environment: str
    log_level: str
    shopify: ShopifySettings
    bigquery: BigQuerySettings


def load_settings() -> Settings:
    """Load application settings from environment variables."""
    return Settings(
        environment=os.getenv("ALPHA60_ENV", _DEFAULT_ENVIRONMENT),
        log_level=os.getenv("ALPHA60_LOG_LEVEL", _DEFAULT_LOG_LEVEL),
        shopify=ShopifySettings(
            shop_domain=os.getenv("ALPHA60_SHOPIFY_SHOP_DOMAIN", ""),
            client_id=os.getenv("ALPHA60_SHOPIFY_CLIENT_ID", ""),
            client_secret=os.getenv("ALPHA60_SHOPIFY_CLIENT_SECRET", ""),
            api_version=os.getenv(
                "ALPHA60_SHOPIFY_API_VERSION",
                _DEFAULT_SHOPIFY_API_VERSION,
            ),
        ),
        bigquery=BigQuerySettings(
            project_id=os.getenv("ALPHA60_BIGQUERY_PROJECT_ID", ""),
            dataset_id=os.getenv("ALPHA60_BIGQUERY_DATASET_ID", ""),
            staging_dataset_id=os.getenv(
                "ALPHA60_BIGQUERY_STAGING_DATASET_ID",
                _DEFAULT_BIGQUERY_STAGING_DATASET_ID,
            ),
            location=os.getenv("ALPHA60_BIGQUERY_LOCATION", _DEFAULT_BIGQUERY_LOCATION),
        ),
    )

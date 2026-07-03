"""Tests for ALPHA60 runtime settings."""

from __future__ import annotations

from importlib import reload

import alpha60.config
from alpha60.config import Settings, load_settings
from alpha60.config.bigquery import BigQuerySettings
from alpha60.config.shopify import ShopifySettings


def test_load_settings_uses_defaults(monkeypatch) -> None:
    """Default settings are used when no environment variables exist."""
    monkeypatch.delenv("ALPHA60_ENV", raising=False)
    monkeypatch.delenv("ALPHA60_LOG_LEVEL", raising=False)
    monkeypatch.delenv("ALPHA60_SHOPIFY_SHOP_DOMAIN", raising=False)
    monkeypatch.delenv("ALPHA60_SHOPIFY_ACCESS_TOKEN", raising=False)
    monkeypatch.delenv("ALPHA60_SHOPIFY_API_VERSION", raising=False)
    monkeypatch.delenv("ALPHA60_BIGQUERY_PROJECT_ID", raising=False)
    monkeypatch.delenv("ALPHA60_BIGQUERY_DATASET_ID", raising=False)
    monkeypatch.delenv("ALPHA60_BIGQUERY_LOCATION", raising=False)

    settings = load_settings()

    assert settings == Settings(
        environment="development",
        log_level="INFO",
        shopify=ShopifySettings(
            shop_domain="",
            access_token="",
            api_version="2025-01",
        ),
        bigquery=BigQuerySettings(
            project_id="",
            dataset_id="",
            location="australia-southeast1",
        ),
    )


def test_load_settings_reads_environment(monkeypatch) -> None:
    """Environment variables override defaults."""
    monkeypatch.setenv("ALPHA60_ENV", "production")
    monkeypatch.setenv("ALPHA60_LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("ALPHA60_SHOPIFY_SHOP_DOMAIN", "alpha60.myshopify.com")
    monkeypatch.setenv("ALPHA60_SHOPIFY_ACCESS_TOKEN", "secret")
    monkeypatch.setenv("ALPHA60_SHOPIFY_API_VERSION", "2025-04")
    monkeypatch.setenv("ALPHA60_BIGQUERY_PROJECT_ID", "alpha60-prod")
    monkeypatch.setenv("ALPHA60_BIGQUERY_DATASET_ID", "raw")
    monkeypatch.setenv("ALPHA60_BIGQUERY_LOCATION", "australia-southeast1")

    settings = load_settings()

    assert settings.environment == "production"
    assert settings.log_level == "DEBUG"
    assert settings.shopify.shop_domain == "alpha60.myshopify.com"
    assert settings.shopify.access_token == "secret"
    assert settings.shopify.api_version == "2025-04"
    assert settings.bigquery.project_id == "alpha60-prod"
    assert settings.bigquery.dataset_id == "raw"
    assert settings.bigquery.location == "australia-southeast1"


def test_module_level_settings_are_loaded(monkeypatch) -> None:
    """The module-level settings object is loaded from the environment."""
    monkeypatch.setenv("ALPHA60_ENV", "test")
    monkeypatch.setenv("ALPHA60_LOG_LEVEL", "WARNING")
    monkeypatch.setenv("ALPHA60_SHOPIFY_SHOP_DOMAIN", "test.myshopify.com")
    monkeypatch.setenv("ALPHA60_SHOPIFY_ACCESS_TOKEN", "test-token")
    monkeypatch.setenv("ALPHA60_BIGQUERY_PROJECT_ID", "alpha60-test")
    monkeypatch.setenv("ALPHA60_BIGQUERY_DATASET_ID", "raw_test")

    reload(alpha60.config)

    assert alpha60.config.settings.environment == "test"
    assert alpha60.config.settings.log_level == "WARNING"
    assert alpha60.config.settings.shopify.shop_domain == "test.myshopify.com"
    assert alpha60.config.settings.shopify.access_token == "test-token"
    assert alpha60.config.settings.bigquery.project_id == "alpha60-test"
    assert alpha60.config.settings.bigquery.dataset_id == "raw_test"
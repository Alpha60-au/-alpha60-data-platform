"""Tests for operational health checks."""

from alpha60.config.bigquery import BigQuerySettings
from alpha60.config.settings import Settings
from alpha60.config.shopify import ShopifySettings
from alpha60.operations.health import (
    HealthCheckResult,
    HealthStatus,
    check_configuration,
)


def test_health_check_result_stores_check_details() -> None:
    """Health check results expose their name, status, and message."""
    result = HealthCheckResult(
        name="config",
        status=HealthStatus.PASS,
        message="Configuration is valid.",
    )

    assert result.name == "config"
    assert result.status == HealthStatus.PASS
    assert result.message == "Configuration is valid."


def test_check_configuration_passes_when_required_settings_are_present() -> None:
    """Configuration health check passes when required settings are present."""
    settings = Settings(
        environment="test",
        log_level="INFO",
        shopify=ShopifySettings(
            shop_domain="test-store.myshopify.com",
            access_token="test-token",
        ),
        bigquery=BigQuerySettings(
            project_id="test-project",
            dataset_id="test_dataset",
        ),
    )

    result = check_configuration(settings=settings)

    assert result == HealthCheckResult(
        name="config",
        status=HealthStatus.PASS,
        message="Configuration is valid.",
    )


def test_check_configuration_fails_when_required_settings_are_missing() -> None:
    """Configuration health check fails when required settings are missing."""
    settings = Settings(
        environment="test",
        log_level="INFO",
        shopify=ShopifySettings(
            shop_domain="",
            access_token="",
        ),
        bigquery=BigQuerySettings(
            project_id="",
            dataset_id="",
        ),
    )

    result = check_configuration(settings=settings)

    assert result.name == "config"
    assert result.status == HealthStatus.FAIL
    assert result.message == (
        "Missing configuration: "
        "shopify.shop_domain, "
        "shopify.access_token, "
        "bigquery.project_id, "
        "bigquery.dataset_id"
    )
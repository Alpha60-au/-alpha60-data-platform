"""Tests for operational health checks."""

from unittest.mock import Mock, patch

from alpha60.config.bigquery import BigQuerySettings
from alpha60.config.settings import Settings
from alpha60.config.shopify import ShopifySettings
from alpha60.operations.health import (
    HealthCheckResult,
    HealthStatus,
    check_bigquery,
    check_configuration,
    check_shopify,
)


def build_settings() -> Settings:
    """Build test settings."""
    return Settings(
        environment="test",
        log_level="INFO",
        shopify=ShopifySettings(
            shop_domain="test-store.myshopify.com",
            client_id="test-client-id",
            client_secret="test-client-secret",
        ),
        bigquery=BigQuerySettings(
            project_id="test-project",
            dataset_id="test_dataset",
        ),
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
    result = check_configuration(settings=build_settings())

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
            client_id="",
            client_secret="",
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
        "shopify.client_id, "
        "shopify.client_secret, "
        "bigquery.project_id, "
        "bigquery.dataset_id"
    )


def test_check_shopify_passes_when_connection_succeeds() -> None:
    """Shopify health check passes when the connection succeeds."""
    with (
        patch("alpha60.operations.health.ShopifyAuthenticator") as authenticator_class,
        patch("alpha60.operations.health.ShopifyClient") as shopify_client_class,
    ):
        authenticator = Mock()
        authenticator.get_access_token.return_value = "temporary-token"
        authenticator_class.return_value = authenticator
        shopify_client_class.return_value.test_connection.return_value = True

        result = check_shopify(settings=build_settings())

    authenticator_class.assert_called_once_with(
        shop_domain="test-store.myshopify.com",
        client_id="test-client-id",
        client_secret="test-client-secret",
    )
    authenticator.get_access_token.assert_called_once_with()
    shopify_client_class.assert_called_once_with(
        shop_domain="test-store.myshopify.com",
        access_token="temporary-token",
        api_version="2025-01",
    )
    assert result == HealthCheckResult(
        name="shopify",
        status=HealthStatus.PASS,
        message="Shopify connection succeeded.",
    )


def test_check_shopify_fails_when_connection_fails() -> None:
    """Shopify health check fails when the connection fails."""
    with (
        patch("alpha60.operations.health.ShopifyAuthenticator") as authenticator_class,
        patch("alpha60.operations.health.ShopifyClient") as shopify_client_class,
    ):
        authenticator = Mock()
        authenticator.get_access_token.return_value = "temporary-token"
        authenticator_class.return_value = authenticator
        shopify_client_class.return_value.test_connection.return_value = False

        result = check_shopify(settings=build_settings())

    assert result == HealthCheckResult(
        name="shopify",
        status=HealthStatus.FAIL,
        message="Shopify connection failed.",
    )


def test_check_bigquery_passes_when_connection_succeeds() -> None:
    """BigQuery health check passes when the connection succeeds."""
    with patch("alpha60.operations.health.GoogleBigQueryClient") as client:
        client.return_value.test_connection.return_value = True

        result = check_bigquery(settings=build_settings())

    assert result == HealthCheckResult(
        name="bigquery",
        status=HealthStatus.PASS,
        message="BigQuery connection succeeded.",
    )


def test_check_bigquery_fails_when_connection_fails() -> None:
    """BigQuery health check fails when the connection fails."""
    with patch("alpha60.operations.health.GoogleBigQueryClient") as client:
        client.return_value.test_connection.return_value = False

        result = check_bigquery(settings=build_settings())

    assert result == HealthCheckResult(
        name="bigquery",
        status=HealthStatus.FAIL,
        message="BigQuery connection failed.",
    )
"""Operational health checks for ALPHA60 dependencies."""

from dataclasses import dataclass
from enum import StrEnum

from alpha60.config.settings import Settings
from alpha60.connectors.shopify.client import ShopifyClient
from alpha60.warehouse.bigquery.config import BigQueryConfig
from alpha60.warehouse.bigquery.google_client import GoogleBigQueryClient


class HealthStatus(StrEnum):
    """Possible health check statuses."""

    PASS = "pass"
    FAIL = "fail"


@dataclass(frozen=True)
class HealthCheckResult:
    """Result of a single operational health check."""

    name: str
    status: HealthStatus
    message: str


def check_configuration(settings: Settings) -> HealthCheckResult:
    """Validate platform configuration."""
    missing: list[str] = []

    if not settings.shopify.shop_domain:
        missing.append("shopify.shop_domain")

    if not settings.shopify.access_token:
        missing.append("shopify.access_token")

    if not settings.bigquery.project_id:
        missing.append("bigquery.project_id")

    if not settings.bigquery.dataset_id:
        missing.append("bigquery.dataset_id")

    if missing:
        return HealthCheckResult(
            name="config",
            status=HealthStatus.FAIL,
            message=f"Missing configuration: {', '.join(missing)}",
        )

    return HealthCheckResult(
        name="config",
        status=HealthStatus.PASS,
        message="Configuration is valid.",
    )


def check_shopify(settings: Settings) -> HealthCheckResult:
    """Validate Shopify connectivity."""
    client = ShopifyClient(
        shop_domain=settings.shopify.shop_domain,
        access_token=settings.shopify.access_token,
        api_version=settings.shopify.api_version,
    )

    if client.test_connection():
        return HealthCheckResult(
            name="shopify",
            status=HealthStatus.PASS,
            message="Shopify connection succeeded.",
        )

    return HealthCheckResult(
        name="shopify",
        status=HealthStatus.FAIL,
        message="Shopify connection failed.",
    )


def check_bigquery(settings: Settings) -> HealthCheckResult:
    """Validate BigQuery connectivity."""
    client = GoogleBigQueryClient(
        config=BigQueryConfig(
            project_id=settings.bigquery.project_id,
            dataset_id=settings.bigquery.dataset_id,
            location=settings.bigquery.location,
        ),
    )

    if client.test_connection():
        return HealthCheckResult(
            name="bigquery",
            status=HealthStatus.PASS,
            message="BigQuery connection succeeded.",
        )

    return HealthCheckResult(
        name="bigquery",
        status=HealthStatus.FAIL,
        message="BigQuery connection failed.",
    )
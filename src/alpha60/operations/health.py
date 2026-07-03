"""Operational health checks for ALPHA60 dependencies."""

from dataclasses import dataclass
from enum import StrEnum

from alpha60.config.settings import Settings


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
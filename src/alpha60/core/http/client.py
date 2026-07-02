"""Generic HTTP client."""

from __future__ import annotations

from alpha60.core.http.config import HTTPConfig


class HTTPClient:
    """Reusable HTTP client for external APIs."""

    def __init__(self, config: HTTPConfig | None = None) -> None:
        """Initialize the HTTP client."""
        self.config = config or HTTPConfig()
"""Generic HTTP client."""

from __future__ import annotations

import httpx

from alpha60.core.http.config import HTTPConfig
from alpha60.core.http.exceptions import (
    AuthenticationError,
    RateLimitError,
    RequestTimeoutError,
    ServerError,
)


class HTTPClient:
    """Reusable HTTP client for external APIs."""

    def __init__(
        self,
        config: HTTPConfig | None = None,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        """Initialize the HTTP client."""
        self.config = config or HTTPConfig()
        self._client = httpx.Client(
            timeout=self.config.timeout,
            transport=transport,
            headers={"User-Agent": self.config.user_agent},
        )

    def get(
        self,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        params: dict[str, str] | None = None,
    ) -> httpx.Response:
        """Perform an HTTP GET request."""
        try:
            response = self._client.get(
                url,
                headers=headers,
                params=params,
            )
        except httpx.TimeoutException as exc:
            raise RequestTimeoutError("HTTP request timed out") from exc

        self._raise_for_status(response)
        return response

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()

    def _raise_for_status(self, response: httpx.Response) -> None:
        """Raise typed exceptions for known HTTP failure responses."""
        if response.status_code in {401, 403}:
            raise AuthenticationError("Authentication failed")

        if response.status_code == 429:
            raise RateLimitError("Rate limit exceeded")

        if 500 <= response.status_code <= 599:
            raise ServerError("Remote server error")
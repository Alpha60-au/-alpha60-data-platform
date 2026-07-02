"""Base interface for all data source connectors."""

from __future__ import annotations

from abc import ABC, abstractmethod

from alpha60.core.models.record import Record


class BaseConnector(ABC):
    """Abstract base class for all source system connectors."""

    @abstractmethod
    def test_connection(self) -> None:
        """Verify connectivity and authentication."""

    @abstractmethod
    def extract(self, **kwargs: object) -> list[Record]:
        """Extract records from the source."""

    @abstractmethod
    def health(self) -> dict[str, str]:
        """Return connector health information."""
"""Application exceptions for the ALPHA60 Data Platform."""

from __future__ import annotations


class Alpha60Error(Exception):
    """Base exception for all ALPHA60 platform errors."""


class ConfigurationError(Alpha60Error):
    """Raised when application configuration is invalid or incomplete."""


class ExternalServiceError(Alpha60Error):
    """Raised when an external service request fails."""


class DataValidationError(Alpha60Error):
    """Raised when data fails platform validation rules."""
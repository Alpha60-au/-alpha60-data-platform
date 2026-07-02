"""Tests for ALPHA60 application exceptions."""

from __future__ import annotations

from alpha60.core.exceptions import (
    Alpha60Error,
    ConfigurationError,
    DataValidationError,
    ExternalServiceError,
)


def test_configuration_error_is_platform_error() -> None:
    assert issubclass(ConfigurationError, Alpha60Error)


def test_external_service_error_is_platform_error() -> None:
    assert issubclass(ExternalServiceError, Alpha60Error)


def test_data_validation_error_is_platform_error() -> None:
    assert issubclass(DataValidationError, Alpha60Error)


def test_platform_error_preserves_message() -> None:
    error = Alpha60Error("Something went wrong")

    assert str(error) == "Something went wrong"
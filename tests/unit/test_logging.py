"""Tests for ALPHA60 logging utilities."""

from __future__ import annotations

import logging

import pytest

from alpha60.core.logging import configure_logging, get_logger


def test_get_logger_returns_named_logger() -> None:
    logger = get_logger("alpha60.test")

    assert logger.name == "alpha60.test"


def test_configure_logging_is_idempotent() -> None:
    root_logger = logging.getLogger()
    root_logger.handlers.clear()

    configure_logging()
    handler_count = len(root_logger.handlers)

    configure_logging()

    assert len(root_logger.handlers) == handler_count


def test_configure_logging_sets_level() -> None:
    configure_logging("DEBUG")

    assert logging.getLogger().level == logging.DEBUG


def test_configure_logging_rejects_invalid_level() -> None:
    with pytest.raises(ValueError, match="Invalid log level"):
        configure_logging("NOT_A_LEVEL")

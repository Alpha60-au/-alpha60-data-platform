"""Tests for ALPHA60 runtime settings."""

from __future__ import annotations

from importlib import reload

import alpha60.config
from alpha60.config import Settings, load_settings


def test_load_settings_uses_defaults(monkeypatch) -> None:
    """Default settings are used when no environment variables exist."""
    monkeypatch.delenv("ALPHA60_ENV", raising=False)
    monkeypatch.delenv("ALPHA60_LOG_LEVEL", raising=False)

    settings = load_settings()

    assert settings == Settings(
        environment="development",
        log_level="INFO",
    )


def test_load_settings_reads_environment(monkeypatch) -> None:
    """Environment variables override defaults."""
    monkeypatch.setenv("ALPHA60_ENV", "production")
    monkeypatch.setenv("ALPHA60_LOG_LEVEL", "DEBUG")

    settings = load_settings()

    assert settings.environment == "production"
    assert settings.log_level == "DEBUG"


def test_module_level_settings_are_loaded(monkeypatch) -> None:
    """The module-level settings object is loaded from the environment."""
    monkeypatch.setenv("ALPHA60_ENV", "test")
    monkeypatch.setenv("ALPHA60_LOG_LEVEL", "WARNING")

    reload(alpha60.config)

    assert alpha60.config.settings.environment == "test"
    assert alpha60.config.settings.log_level == "WARNING"
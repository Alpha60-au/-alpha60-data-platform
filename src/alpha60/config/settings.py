"""Runtime settings for the ALPHA60 Data Platform."""

from __future__ import annotations

from dataclasses import dataclass
import os


_DEFAULT_ENVIRONMENT = "development"
_DEFAULT_LOG_LEVEL = "INFO"


@dataclass(frozen=True)
class Settings:
    """Application settings loaded from the runtime environment."""

    environment: str
    log_level: str


def load_settings() -> Settings:
    """Load application settings from environment variables."""
    return Settings(
        environment=os.getenv("ALPHA60_ENV", _DEFAULT_ENVIRONMENT),
        log_level=os.getenv("ALPHA60_LOG_LEVEL", _DEFAULT_LOG_LEVEL),
    )
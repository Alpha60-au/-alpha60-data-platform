"""Configuration utilities for the ALPHA60 Data Platform."""

from alpha60.config.settings import Settings, load_settings

settings = load_settings()

__all__ = [
    "Settings",
    "load_settings",
    "settings",
]
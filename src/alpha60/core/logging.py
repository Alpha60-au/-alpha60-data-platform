"""Logging utilities for the ALPHA60 Data Platform.

All application modules should obtain loggers through this module rather than
configuring Python logging directly.
"""

from __future__ import annotations

import logging
import os

_DEFAULT_LOG_LEVEL = "INFO"
_LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"


def configure_logging(log_level: str | None = None) -> None:
    """Configure application logging once."""
    resolved_level = log_level
    if resolved_level is None:
        resolved_level = os.getenv("ALPHA60_LOG_LEVEL") or _DEFAULT_LOG_LEVEL

    resolved_level = resolved_level.upper()
    numeric_level = logging.getLevelName(resolved_level)

    if not isinstance(numeric_level, int):
        msg = f"Invalid log level: {resolved_level}"
        raise ValueError(msg)

    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    if not root_logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(_LOG_FORMAT))
        root_logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """Return a configured logger for the given module name."""
    configure_logging()
    return logging.getLogger(name)
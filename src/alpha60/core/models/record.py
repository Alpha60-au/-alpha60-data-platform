"""Shared data model for extracted records."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(slots=True, frozen=True)
class Record:
    """Represents a single extracted record from a source system."""

    source: str
    entity: str
    record_id: str
    extracted_at: datetime
    payload: dict[str, Any]
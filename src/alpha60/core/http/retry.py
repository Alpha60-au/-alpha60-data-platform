"""Retry policy for the generic HTTP client."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class RetryPolicy:
    """Defines retry behaviour for transient HTTP failures."""

    max_attempts: int = 3
    backoff_factor: float = 1.0

    def backoff_delay(self, attempt: int) -> float:
        """Return the exponential backoff delay for an attempt.

        Attempt numbering starts at 1.
        """
        if attempt < 1:
            raise ValueError("attempt must be >= 1")

        return self.backoff_factor * (2 ** (attempt - 1))
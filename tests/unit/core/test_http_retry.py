"""Tests for HTTP retry policy."""

from dataclasses import FrozenInstanceError

import pytest

from alpha60.core.http.retry import RetryPolicy


def test_default_retry_policy() -> None:
    policy = RetryPolicy()

    assert policy.max_attempts == 3
    assert policy.backoff_factor == 1.0


def test_custom_retry_policy() -> None:
    policy = RetryPolicy(max_attempts=5, backoff_factor=2.0)

    assert policy.max_attempts == 5
    assert policy.backoff_factor == 2.0


def test_backoff_delay_uses_exponential_backoff() -> None:
    policy = RetryPolicy(backoff_factor=1.0)

    assert policy.backoff_delay(1) == 1.0
    assert policy.backoff_delay(2) == 2.0
    assert policy.backoff_delay(3) == 4.0


def test_backoff_delay_uses_custom_backoff_factor() -> None:
    policy = RetryPolicy(backoff_factor=0.5)

    assert policy.backoff_delay(1) == 0.5
    assert policy.backoff_delay(2) == 1.0
    assert policy.backoff_delay(3) == 2.0


def test_backoff_delay_rejects_invalid_attempt() -> None:
    policy = RetryPolicy()

    with pytest.raises(ValueError, match="attempt must be >= 1"):
        policy.backoff_delay(0)


def test_retry_policy_is_immutable() -> None:
    policy = RetryPolicy()

    with pytest.raises(FrozenInstanceError):
        policy.max_attempts = 5  # type: ignore[misc]
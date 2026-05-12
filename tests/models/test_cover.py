"""Tests for myviolet.models.cover."""

from __future__ import annotations

from myviolet.enums import CoverState
from myviolet.models.cover import Cover


def test_from_raw_open(get_readings_seed: dict) -> None:
    cover = Cover.from_raw(get_readings_seed)
    assert cover is not None
    assert cover.state is CoverState.OPEN


def test_from_raw_missing_returns_none() -> None:
    assert Cover.from_raw({}) is None

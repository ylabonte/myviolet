"""Shared pytest fixtures for the myviolet test suite.

The `getReadings_*.json` files served by these fixtures were captured from
the vendor-owned public demo controller at <https://demo.myviolet.de/>.
See `tests/fixtures/README.md` for provenance and sanitisation guidance.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _load_json(name: str) -> dict[str, Any]:
    with (FIXTURES_DIR / name).open(encoding="utf-8") as fh:
        return json.load(fh)  # type: ignore[no-any-return]


@pytest.fixture
def get_readings_seed() -> dict[str, Any]:
    """Full /getReadings?ALL,DOSAGE,RUNTIMES capture from demo.myviolet.de."""
    return _load_json("getReadings_seed.json")


@pytest.fixture
def get_readings_selective() -> dict[str, Any]:
    """A selective /getReadings?pH_value,PUMP,COVER_STATE response."""
    return _load_json("getReadings_selective.json")

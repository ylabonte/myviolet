"""Tests for myviolet.models.chemistry."""

from __future__ import annotations

import pytest

from myviolet.models.chemistry import WaterChemistry


def test_from_raw_complete(get_readings_seed: dict) -> None:
    chem = WaterChemistry.from_raw(get_readings_seed)
    assert chem.ph is not None
    assert chem.ph.value == pytest.approx(7.307)
    assert chem.ph.unit == "pH"
    assert chem.ph.min == pytest.approx(7.3)
    assert chem.ph.max == pytest.approx(7.32)

    assert chem.orp is not None
    assert chem.orp.value == pytest.approx(787.4)
    assert chem.orp.unit == "mV"

    assert chem.chlorine is not None
    assert chem.chlorine.value == pytest.approx(0.29)
    assert chem.chlorine.unit == "mg/L"


def test_from_raw_missing_chlorine_returns_none() -> None:
    raw = {"pH_value": 7.3, "orp_value": 700.0}
    chem = WaterChemistry.from_raw(raw)
    assert chem.ph is not None
    assert chem.orp is not None
    assert chem.chlorine is None

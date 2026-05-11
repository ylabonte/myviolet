"""Tests for myviolet.readings.VioletReadings."""

from __future__ import annotations

from myviolet.enums import CoverState, PvSurplusState
from myviolet.readings import VioletReadings


def test_wraps_raw_dict(get_readings_seed: dict) -> None:
    snapshot = VioletReadings(get_readings_seed)
    # `.raw` exposes the same contents but as a read-only mapping
    assert dict(snapshot.raw) == get_readings_seed


def test_water_chemistry(get_readings_seed: dict) -> None:
    snapshot = VioletReadings(get_readings_seed)
    assert snapshot.water_chemistry.ph is not None
    assert snapshot.water_chemistry.ph.value > 0


def test_onewire_collection(get_readings_seed: dict) -> None:
    snapshot = VioletReadings(get_readings_seed)
    assert len(snapshot.onewire_sensors) == 12


def test_pump(get_readings_seed: dict) -> None:
    snapshot = VioletReadings(get_readings_seed)
    assert snapshot.pump is not None
    assert snapshot.pump.state.is_on


def test_cover(get_readings_seed: dict) -> None:
    snapshot = VioletReadings(get_readings_seed)
    assert snapshot.cover is not None
    assert snapshot.cover.state is CoverState.OPEN


def test_dosing(get_readings_seed: dict) -> None:
    snapshot = VioletReadings(get_readings_seed)
    assert "CL" in snapshot.dosing_channels
    assert "ELO_REV" in snapshot.dosing_channels  # observed-but-undocumented


def test_extension_relays(get_readings_seed: dict) -> None:
    snapshot = VioletReadings(get_readings_seed)
    assert set(snapshot.extension_relays.keys()) == {1, 2}


def test_pv_surplus(get_readings_seed: dict) -> None:
    snapshot = VioletReadings(get_readings_seed)
    assert snapshot.pv_surplus is not None
    assert snapshot.pv_surplus.state is PvSurplusState.OFF


def test_system_info(get_readings_seed: dict) -> None:
    snapshot = VioletReadings(get_readings_seed)
    assert snapshot.system_info.sw_version == "1.1.9"


def test_hardware_profile(get_readings_seed: dict) -> None:
    snapshot = VioletReadings(get_readings_seed)
    profile = snapshot.hardware_profile
    assert profile.has_pump
    assert profile.has_dmx
    assert len(profile.onewire_active_indices) == 10


def test_lazy_memoization(get_readings_seed: dict) -> None:
    """Repeated property access returns the same object (memoized)."""
    snapshot = VioletReadings(get_readings_seed)
    first = snapshot.pump
    second = snapshot.pump
    assert first is second


def test_empty_dict_returns_none_for_optional_views() -> None:
    snapshot = VioletReadings({})
    assert snapshot.pump is None
    assert snapshot.cover is None
    assert snapshot.dosing_channels == {}
    assert snapshot.extension_relays == {}

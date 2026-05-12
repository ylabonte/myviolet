"""Tests for myviolet.hardware — installed-hardware inference."""

from __future__ import annotations

import pytest

from myviolet.hardware import HardwareProfile


def test_from_seed_full_inventory(get_readings_seed: dict) -> None:
    profile = HardwareProfile.from_raw(get_readings_seed)
    # Demo controller has 10 configured 1-wire sensors (out of 12 slots)
    assert profile.onewire_active_indices == {1, 2, 3, 4, 5, 6, 7, 8, 9, 10}
    assert profile.dosing_channel_codes == {"CL", "ELO", "ELO_REV", "PHM", "PHP", "FLOC"}
    assert profile.extension_buses == {1, 2}
    assert profile.extension_relays_per_bus == {1: 8, 2: 8}
    assert profile.has_dmx is True
    assert profile.has_pump is True
    assert profile.has_heater is True
    assert profile.has_solar is True
    assert profile.has_light is True
    assert profile.has_backwash is True
    assert profile.has_cover is True
    assert profile.has_pv_surplus is True
    assert profile.digital_input_count == 12
    assert profile.can_empty_input_count == 4


def test_from_minimal() -> None:
    profile = HardwareProfile.from_raw({"PUMP": 0})
    assert profile.has_pump is True
    assert profile.has_heater is False
    assert profile.onewire_active_indices == set()
    assert profile.dosing_channel_codes == set()
    assert profile.extension_buses == set()
    assert profile.has_dmx is False


def test_from_empty() -> None:
    profile = HardwareProfile.from_raw({})
    assert profile.has_pump is False
    assert profile.digital_input_count == 0


def test_containers_are_immutable(get_readings_seed: dict) -> None:
    """`frozen=True` only freezes the attribute bindings, not container contents.
    The set/dict fields must themselves be immutable so callers can't mutate a
    snapshot in-place."""
    profile = HardwareProfile.from_raw(get_readings_seed)
    with pytest.raises(AttributeError):
        profile.onewire_active_indices.add(99)  # type: ignore[attr-defined]
    with pytest.raises(AttributeError):
        profile.dosing_channel_codes.add("ZZ")  # type: ignore[attr-defined]
    with pytest.raises(TypeError):
        profile.extension_relays_per_bus[3] = 8  # type: ignore[index]

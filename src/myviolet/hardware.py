"""Installed-hardware inference from a `/getReadings` response.

The Violet controller does not expose a dedicated `/getHardwareInfo`
endpoint, so installed hardware must be inferred from which keys appear in
the readings snapshot. Most outputs are "present" iff their canonical state
key is in the dict; 1-wire sensors only count as "active" when the state
is anything other than `NO_SENSOR_CONFIGURED`.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any

from .constants import DOSING_CHANNELS
from .enums import OnewireState

_EMPTY_INT_INT_MAP: Mapping[int, int] = MappingProxyType({})


@dataclass(frozen=True, slots=True)
class HardwareProfile:
    """A summary of which controller hardware is present and configured."""

    has_pump: bool
    has_heater: bool
    has_solar: bool
    has_light: bool
    has_refill: bool
    has_eco: bool
    has_backwash: bool
    has_cover: bool
    has_pv_surplus: bool
    has_dmx: bool
    onewire_active_indices: frozenset[int] = field(default_factory=frozenset)
    dosing_channel_codes: frozenset[str] = field(default_factory=frozenset)
    extension_buses: frozenset[int] = field(default_factory=frozenset)
    extension_relays_per_bus: Mapping[int, int] = _EMPTY_INT_INT_MAP
    digital_input_count: int = 0
    can_empty_input_count: int = 0
    analog_sensor_count: int = 0

    @classmethod
    def from_raw(cls, raw: dict[str, Any]) -> HardwareProfile:
        return cls(
            has_pump="PUMP" in raw,
            has_heater="HEATER" in raw,
            has_solar="SOLAR" in raw,
            has_light="LIGHT" in raw,
            has_refill="REFILL" in raw,
            has_eco="ECO" in raw,
            has_backwash="BACKWASH" in raw,
            has_cover="COVER_STATE" in raw,
            has_pv_surplus="PVSURPLUS" in raw,
            has_dmx=any(f"DMX_SCENE{i}" in raw for i in range(1, 13)),
            onewire_active_indices=_active_onewire_indices(raw),
            dosing_channel_codes=_present_dosing_codes(raw),
            extension_buses=_present_extension_buses(raw),
            extension_relays_per_bus=_extension_relay_counts(raw),
            digital_input_count=sum(1 for i in range(1, 13) if f"INPUT{i}" in raw),
            can_empty_input_count=sum(1 for i in range(1, 5) if f"INPUT_CE{i}" in raw),
            analog_sensor_count=sum(1 for i in range(1, 7) if f"ADC{i}_value" in raw),
        )


def _active_onewire_indices(raw: dict[str, Any]) -> frozenset[int]:
    return frozenset(
        idx
        for idx in range(1, 13)
        if (state := raw.get(f"onewire{idx}_state")) is not None
        and state != OnewireState.NO_SENSOR_CONFIGURED.value
    )


def _present_dosing_codes(raw: dict[str, Any]) -> frozenset[str]:
    return frozenset(
        code for number, code in DOSING_CHANNELS.items() if f"DOS_{number}_{code}" in raw
    )


def _present_extension_buses(raw: dict[str, Any]) -> frozenset[int]:
    return frozenset(bus for bus in (1, 2) if any(f"EXT{bus}_{i}" in raw for i in range(1, 9)))


def _extension_relay_counts(raw: dict[str, Any]) -> Mapping[int, int]:
    counts: dict[int, int] = {}
    for bus in (1, 2):
        count = sum(1 for i in range(1, 9) if f"EXT{bus}_{i}" in raw)
        if count:
            counts[bus] = count
    return MappingProxyType(counts)

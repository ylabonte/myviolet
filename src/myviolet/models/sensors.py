"""Sensor typed views: analog, impulse, and 1-wire."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..enums import OnewireState
from ._common import MeasuredValue


@dataclass(frozen=True, slots=True)
class AnalogSensor:
    """One of the 6 analog sensor channels (`ADC1`-`ADC6`)."""

    index: int
    value: float


@dataclass(frozen=True, slots=True)
class ImpulseInput:
    """One of the 2 impulse inputs (`IMP1` flow switch, `IMP2` flow pump)."""

    index: int
    value: float


@dataclass(frozen=True, slots=True)
class OneWireSensor:
    """A single 1-wire temperature sensor (12 slots, only configured ones)."""

    index: int
    state: OnewireState
    rom_code: str
    value: float
    unit: str
    value_min: float | None = None
    value_max: float | None = None

    @property
    def measured(self) -> MeasuredValue:
        """Expose the reading as a `MeasuredValue` for uniform processing."""
        return MeasuredValue(
            value=self.value,
            unit=self.unit,
            min=self.value_min,
            max=self.value_max,
        )


def collect_analog_sensors(raw: dict[str, Any]) -> dict[int, AnalogSensor]:
    """Return ADC sensors keyed by index (1-6), present-only."""
    result: dict[int, AnalogSensor] = {}
    for idx in range(1, 7):
        value = raw.get(f"ADC{idx}_value")
        if value is None:
            continue
        result[idx] = AnalogSensor(index=idx, value=float(value))
    return result


def collect_impulse_inputs(raw: dict[str, Any]) -> dict[int, ImpulseInput]:
    """Return impulse inputs keyed by index (1-2), present-only."""
    result: dict[int, ImpulseInput] = {}
    for idx in range(1, 3):
        value = raw.get(f"IMP{idx}_value")
        if value is None:
            continue
        result[idx] = ImpulseInput(index=idx, value=float(value))
    return result


def collect_onewire_sensors(raw: dict[str, Any]) -> dict[int, OneWireSensor]:
    """Return 1-wire sensors keyed by index (1-12), present-only.

    A "present" sensor is one whose ``state`` key appears in `raw`. The
    controller still emits the slot's fields (with ``state =
    NO_SENSOR_CONFIGURED``, ``rcode = "0"``) when nothing is plugged into a
    given slot, so we keep those entries — callers can filter by `state`
    if they only want active sensors.
    """
    result: dict[int, OneWireSensor] = {}
    for idx in range(1, 13):
        state_raw = raw.get(f"onewire{idx}_state")
        if state_raw is None:
            continue
        value_raw = raw.get(f"onewire{idx}_value")
        if value_raw is None:
            continue
        result[idx] = OneWireSensor(
            index=idx,
            state=OnewireState(str(state_raw)),
            rom_code=str(raw.get(f"onewire{idx}_rcode", "")),
            value=float(value_raw),
            unit="°C",
            value_min=_maybe_float(raw.get(f"onewire{idx}_value_min")),
            value_max=_maybe_float(raw.get(f"onewire{idx}_value_max")),
        )
    return result


def _maybe_float(value: Any) -> float | None:
    return None if value is None else float(value)

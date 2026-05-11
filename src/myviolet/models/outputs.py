"""Binary output typed views — pump, heater, solar, light, refill, eco, backwash.

Most outputs share the `OutputBase` shape (state + last_on + last_off +
runtime). The pump exposes 4 RPM-speed sub-outputs; the heater exposes an
optional postrun-timer remaining duration.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

from ..enums import OutputState
from ..parsers import parse_optional_seconds, parse_runtime_string
from ._common import OutputBase


@dataclass(frozen=True, slots=True)
class PumpSpeed:
    """One of the pump's 4 speed sub-outputs (RPM 0=stop, 1-3=speeds).

    The vendor documents `PUMP_RPM_*_LAST_ON/OFF` as always `"00:00:00"` and
    not useful, so they are surfaced as `None` rather than parsed.
    """

    rpm: int
    state: OutputState
    runtime: timedelta
    last_on: datetime | None = None
    last_off: datetime | None = None


@dataclass(frozen=True, slots=True)
class Pump:
    """Main pump output plus its 4 speed sub-outputs."""

    state: OutputState
    last_on: datetime | None
    last_off: datetime | None
    runtime: timedelta
    speeds: dict[int, PumpSpeed] = field(default_factory=dict)

    @classmethod
    def from_raw(cls, raw: dict[str, Any]) -> Pump | None:
        base = OutputBase.from_raw(raw, "PUMP")
        if base is None:
            return None
        speeds: dict[int, PumpSpeed] = {}
        for rpm in range(4):
            state_raw = raw.get(f"PUMP_RPM_{rpm}")
            if state_raw is None:
                continue
            try:
                state = OutputState(int(state_raw))
            except ValueError:
                # Forward-compat: skip unknown firmware enum values rather than crash.
                continue
            speeds[rpm] = PumpSpeed(
                rpm=rpm,
                state=state,
                runtime=parse_runtime_string(raw.get(f"PUMP_RPM_{rpm}_RUNTIME", "00h 00m 00s")),
            )
        return cls(
            state=base.state,
            last_on=base.last_on,
            last_off=base.last_off,
            runtime=base.runtime,
            speeds=speeds,
        )


@dataclass(frozen=True, slots=True)
class Heater:
    """Heater output, including the optional postrun-timer remaining time."""

    state: OutputState
    last_on: datetime | None
    last_off: datetime | None
    runtime: timedelta
    postrun_remaining: timedelta | None = None

    @classmethod
    def from_raw(cls, raw: dict[str, Any]) -> Heater | None:
        base = OutputBase.from_raw(raw, "HEATER")
        if base is None:
            return None
        return cls(
            state=base.state,
            last_on=base.last_on,
            last_off=base.last_off,
            runtime=base.runtime,
            postrun_remaining=parse_optional_seconds(raw.get("HEATER_POSTRUN_TIME")),
        )


@dataclass(frozen=True, slots=True)
class Solar:
    """Solar circulation output."""

    state: OutputState
    last_on: datetime | None
    last_off: datetime | None
    runtime: timedelta

    @classmethod
    def from_raw(cls, raw: dict[str, Any]) -> Solar | None:
        base = OutputBase.from_raw(raw, "SOLAR")
        return None if base is None else cls(base.state, base.last_on, base.last_off, base.runtime)


@dataclass(frozen=True, slots=True)
class Light:
    """Light output."""

    state: OutputState
    last_on: datetime | None
    last_off: datetime | None
    runtime: timedelta

    @classmethod
    def from_raw(cls, raw: dict[str, Any]) -> Light | None:
        base = OutputBase.from_raw(raw, "LIGHT")
        return None if base is None else cls(base.state, base.last_on, base.last_off, base.runtime)


@dataclass(frozen=True, slots=True)
class Refill:
    """Refill output."""

    state: OutputState
    last_on: datetime | None
    last_off: datetime | None
    runtime: timedelta

    @classmethod
    def from_raw(cls, raw: dict[str, Any]) -> Refill | None:
        base = OutputBase.from_raw(raw, "REFILL")
        return None if base is None else cls(base.state, base.last_on, base.last_off, base.runtime)


@dataclass(frozen=True, slots=True)
class Eco:
    """Eco-mode output."""

    state: OutputState
    last_on: datetime | None
    last_off: datetime | None
    runtime: timedelta

    @classmethod
    def from_raw(cls, raw: dict[str, Any]) -> Eco | None:
        base = OutputBase.from_raw(raw, "ECO")
        return None if base is None else cls(base.state, base.last_on, base.last_off, base.runtime)


@dataclass(frozen=True, slots=True)
class Backwash:
    """Backwash output (the running-or-not flag; richer status in `BackwashStatus`)."""

    state: OutputState
    last_on: datetime | None
    last_off: datetime | None
    runtime: timedelta

    @classmethod
    def from_raw(cls, raw: dict[str, Any]) -> Backwash | None:
        base = OutputBase.from_raw(raw, "BACKWASH")
        return None if base is None else cls(base.state, base.last_on, base.last_off, base.runtime)


@dataclass(frozen=True, slots=True)
class BackwashRinse:
    """Backwash-rinse output."""

    state: OutputState
    last_on: datetime | None
    last_off: datetime | None
    runtime: timedelta

    @classmethod
    def from_raw(cls, raw: dict[str, Any]) -> BackwashRinse | None:
        base = OutputBase.from_raw(raw, "BACKWASHRINSE")
        return None if base is None else cls(base.state, base.last_on, base.last_off, base.runtime)


__all__ = [
    "Backwash",
    "BackwashRinse",
    "Eco",
    "Heater",
    "Light",
    "Pump",
    "PumpSpeed",
    "Refill",
    "Solar",
]

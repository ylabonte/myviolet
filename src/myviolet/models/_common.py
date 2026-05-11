"""Shared base types for the typed view layer."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from ..enums import OutputState
from ..parsers import parse_epoch_seconds, parse_runtime_string


@dataclass(frozen=True, slots=True)
class MeasuredValue:
    """A sensor reading plus its daily min/max envelope.

    Many sensor categories (water chemistry, 1-wire temperatures, analog
    inputs) expose ``<KEY>_value``, ``<KEY>_value_min``, ``<KEY>_value_max``
    triplets. `MeasuredValue` is the typed wrapper.
    """

    value: float
    unit: str
    min: float | None = None
    max: float | None = None

    @classmethod
    def from_raw(
        cls,
        raw: dict[str, Any],
        key_base: str,
        *,
        unit: str,
    ) -> MeasuredValue | None:
        """Assemble from `<key_base>_value`/`_value_min`/`_value_max` siblings.

        Returns ``None`` when the canonical ``<key_base>_value`` key is absent,
        which lets callers distinguish "sensor not installed" from "value zero".
        """
        value = raw.get(f"{key_base}_value")
        if value is None:
            return None
        return cls(
            value=float(value),
            unit=unit,
            min=_maybe_float(raw.get(f"{key_base}_value_min")),
            max=_maybe_float(raw.get(f"{key_base}_value_max")),
        )


@dataclass(frozen=True, slots=True)
class OutputBase:
    """Shared shape for the ~30 binary outputs (pump, heater, relays, ...).

    Every documented binary output (PUMP, HEATER, SOLAR, LIGHT, REFILL, ECO,
    BACKWASH, BACKWASHRINSE, EXT1_*, EXT2_*) emits the same four siblings:
    a state integer, two epoch-seconds timestamps, and a runtime string.
    """

    state: OutputState
    last_on: datetime | None
    last_off: datetime | None
    runtime: timedelta

    @classmethod
    def from_raw(cls, raw: dict[str, Any], key_base: str) -> OutputBase | None:
        """Assemble from ``<key_base>``, ``_LAST_ON``, ``_LAST_OFF``, ``_RUNTIME``.

        Returns ``None`` when the canonical state key is absent (output not
        installed) **or** when the controller emits an `OutputState` value
        not in our documented enum — that lets the typed view layer stay
        forward-compatible with future firmware revisions instead of
        crashing the entire snapshot.
        """
        state_raw = raw.get(key_base)
        if state_raw is None:
            return None
        try:
            state = OutputState(int(state_raw))
        except (ValueError, TypeError):
            return None
        runtime_raw = raw.get(f"{key_base}_RUNTIME", "00h 00m 00s")
        try:
            runtime = parse_runtime_string(runtime_raw)
        except ValueError:
            runtime = timedelta(0)
        return cls(
            state=state,
            last_on=parse_epoch_seconds(raw.get(f"{key_base}_LAST_ON")),
            last_off=parse_epoch_seconds(raw.get(f"{key_base}_LAST_OFF")),
            runtime=runtime,
        )


def _maybe_float(value: Any) -> float | None:
    if value is None:
        return None
    return float(value)

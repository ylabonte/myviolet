"""Dosing channel typed views.

Each channel has a numeric position (1-6) and a textual code (`CL`, `ELO`,
`ELO_REV`, `PHM`, `PHP`, `FLOC`). The vendor spec documents channels 1, 2,
4, 5, 6 and skips 3 — but the live demo controller exposes a
`DOS_3_ELO_REV` reverse-dosing channel, so we include it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

from ..enums import DosingType, OutputState
from ..parsers import (
    parse_epoch_milliseconds,
    parse_epoch_seconds,
    parse_runtime_string,
)

# Channel number → textual code. Documented in the vendor spec plus the
# observed `DOS_3_ELO_REV` reverse-dosing channel.
_CHANNELS: dict[int, str] = {
    1: "CL",
    2: "ELO",
    3: "ELO_REV",
    4: "PHM",
    5: "PHP",
    6: "FLOC",
}


@dataclass(frozen=True, slots=True)
class DosingChannel:
    """One dosing channel. Optional DOSAGE-keyword fields default to `None`."""

    code: str
    channel_number: int
    state: OutputState
    last_on: datetime | None
    last_off: datetime | None
    runtime: timedelta
    daily_amount_ml: int | None = None
    total_can_amount_ml: int | None = None
    last_can_reset: datetime | None = None
    enabled: bool | None = None
    type: DosingType | None = None
    state_blocks: list[str] = field(default_factory=list)


def collect_dosing_channels(raw: dict[str, Any]) -> dict[str, DosingChannel]:
    """Return dosing channels keyed by code (`CL`, `ELO`, ...), present-only."""
    result: dict[str, DosingChannel] = {}
    for number, code in _CHANNELS.items():
        base = f"DOS_{number}_{code}"
        state_raw = raw.get(base)
        if state_raw is None:
            continue
        result[code] = DosingChannel(
            code=code,
            channel_number=number,
            state=OutputState(int(state_raw)),
            last_on=parse_epoch_seconds(raw.get(f"{base}_LAST_ON")),
            last_off=parse_epoch_seconds(raw.get(f"{base}_LAST_OFF")),
            runtime=parse_runtime_string(raw.get(f"{base}_RUNTIME", "00h 00m 00s")),
            daily_amount_ml=_maybe_int(raw.get(f"{base}_DAILY_DOSING_AMOUNT_ML")),
            total_can_amount_ml=_maybe_int(raw.get(f"{base}_TOTAL_CAN_AMOUNT_ML")),
            last_can_reset=parse_epoch_milliseconds(raw.get(f"{base}_LAST_CAN_RESET")),
            enabled=_maybe_bool(raw.get(f"{base}_USE")),
            type=_maybe_dosing_type(raw.get(f"{base}_TYPE")),
            state_blocks=list(raw.get(f"{base}_STATE", []) or []),
        )
    return result


def _maybe_int(value: Any) -> int | None:
    return None if value is None else int(value)


def _maybe_bool(value: Any) -> bool | None:
    return None if value is None else bool(int(value))


def _maybe_dosing_type(value: Any) -> DosingType | None:
    return None if value is None else DosingType(int(value))

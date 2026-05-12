"""Mixed system-state typed views: overflow, backwash status, bathing AI, PV surplus."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from ..enums import PvSurplusState, SimpleOnOff, YesNo
from ..parsers import parse_epoch_seconds


@dataclass(frozen=True, slots=True)
class OverflowState:
    """Overflow-vessel control flags (dryrun, overfill, refill triggers)."""

    dryrun: SimpleOnOff
    overfill: SimpleOnOff
    refill: SimpleOnOff

    @classmethod
    def from_raw(cls, raw: dict[str, Any]) -> OverflowState | None:
        if "OVERFLOW_DRYRUN_STATE" not in raw:
            return None
        try:
            return cls(
                dryrun=SimpleOnOff(raw["OVERFLOW_DRYRUN_STATE"]),
                overfill=SimpleOnOff(raw.get("OVERFLOW_OVERFILL_STATE", "OFF")),
                refill=SimpleOnOff(raw.get("OVERFLOW_REFILL_STATE", "OFF")),
            )
        except ValueError:
            # Forward-compat: an unknown firmware value on any flag drops the
            # whole snapshot rather than half-populating it, matching the
            # `Cover.from_raw` / `OutputBase.from_raw` pattern.
            return None


@dataclass(frozen=True, slots=True)
class BackwashStatus:
    """Backwash-process status flags plus the free-form raw state string.

    The vendor's `BACKWASH_STATE` field mixes several different message types
    (e.g. `NEXT_BW_IN 2 BW_DAY5`, `BW_RUNNING_SINCE 123`). Rather than try to
    parse all variants, we expose it verbatim as `raw_state`.
    """

    delay_running: bool
    delay_started_at: datetime | None
    last_auto_run: datetime | None
    last_manual_run: datetime | None
    omni_moving: YesNo | None
    omni_state: str | None
    step: int
    raw_state: str

    @classmethod
    def from_raw(cls, raw: dict[str, Any]) -> BackwashStatus | None:
        if "BACKWASH_STATE" not in raw:
            return None
        return cls(
            delay_running=_parse_yesno(raw.get("BACKWASH_DELAY_RUNNING", "NO")) is YesNo.YES,
            delay_started_at=parse_epoch_seconds(raw.get("BACKWASH_DELAY_TIMESTAMP")),
            last_auto_run=parse_epoch_seconds(raw.get("BACKWASH_LAST_AUTO_RUN")),
            last_manual_run=parse_epoch_seconds(raw.get("BACKWASH_LAST_MANUAL_RUN")),
            omni_moving=_parse_yesno(raw.get("BACKWASH_OMNI_MOVING")),
            omni_state=raw.get("BACKWASH_OMNI_STATE"),
            step=int(raw.get("BACKWASH_STEP", 0)),
            raw_state=str(raw["BACKWASH_STATE"]),
        )


@dataclass(frozen=True, slots=True)
class BathingAi:
    """Bathing-AI overflow-vessel surveillance state.

    The vendor's spec documents `surveillance_state` as YES/NO; the live
    controller emits a third value (`TRIGGERED`) too, so we keep it as a
    plain string instead of a strict enum.
    """

    surveillance_state: str
    start_level: float
    last_level: float
    pump_state: SimpleOnOff | None
    pump_started_at: datetime | None

    @classmethod
    def from_raw(cls, raw: dict[str, Any]) -> BathingAi | None:
        if "BATHING_AI_SURVEILLANCE_STATE" not in raw:
            return None
        return cls(
            surveillance_state=str(raw["BATHING_AI_SURVEILLANCE_STATE"]),
            start_level=float(raw.get("BATHING_AI_START_LEVEL", 0.0)),
            last_level=float(raw.get("BATHING_AI_LAST_LEVEL", 0.0)),
            pump_state=_parse_simple_onoff(raw.get("BATHING_AI_PUMP_STATE", "OFF")),
            pump_started_at=parse_epoch_seconds(raw.get("BATHING_AI_PUMP_TIMESTAMP")),
        )


@dataclass(frozen=True, slots=True)
class PvSurplus:
    """PV-surplus function: off, on-by-input, or on-by-HTTP."""

    state: PvSurplusState

    @classmethod
    def from_raw(cls, raw: dict[str, Any]) -> PvSurplus | None:
        value = raw.get("PVSURPLUS")
        if value is None:
            return None
        try:
            return cls(state=PvSurplusState(int(value)))
        except ValueError:
            # Forward-compat: unknown firmware enum value drops the snapshot
            # rather than crashing parsing of unrelated readings.
            return None


def _parse_yesno(value: Any) -> YesNo | None:
    if value is None:
        return None
    try:
        return YesNo(value)
    except ValueError:
        return None


def _parse_simple_onoff(value: Any) -> SimpleOnOff | None:
    if value is None:
        return None
    try:
        return SimpleOnOff(value)
    except ValueError:
        return None

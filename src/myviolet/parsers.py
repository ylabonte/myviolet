"""Format parsers for Violet API string values.

The Violet controller returns timestamps and durations in several distinct
formats — Unix epoch seconds, Unix epoch milliseconds, "04h 33m 12s" runtime
strings, "250d 11h 48m" uptime strings, and the legacy "HH:MM:SS" used by
some pump-RPM fields. Plus the `HEATER_POSTRUN_TIME` field uses the literal
string `"NONE"` as a "timer expired" sentinel. Each format gets a dedicated
parser here so the typed view modules can stay focused.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime, timedelta

_RUNTIME_RE = re.compile(r"^\s*(\d+)h\s+(\d+)m\s+(\d+)s\s*$")
_HMS_RE = re.compile(r"^\s*(\d+):(\d+):(\d+)\s*$")
_UPTIME_RE = re.compile(r"^\s*(\d+)d\s+(\d+)h\s+(\d+)m\s*$")


def parse_runtime_string(raw: str) -> timedelta:
    """Parse a runtime string like ``"04h 33m 12s"`` into a `timedelta`."""
    match = _RUNTIME_RE.match(raw)
    if match is None:
        raise ValueError(f"invalid runtime string: {raw!r}")
    hours, minutes, seconds = (int(g) for g in match.groups())
    return timedelta(hours=hours, minutes=minutes, seconds=seconds)


def parse_hms_string(raw: str) -> timedelta:
    """Parse a legacy ``HH:MM:SS`` duration into a `timedelta`."""
    match = _HMS_RE.match(raw)
    if match is None:
        raise ValueError(f"invalid HH:MM:SS string: {raw!r}")
    hours, minutes, seconds = (int(g) for g in match.groups())
    return timedelta(hours=hours, minutes=minutes, seconds=seconds)


def parse_uptime_string(raw: str) -> timedelta:
    """Parse the CPU uptime string ``"250d 11h 48m"`` into a `timedelta`."""
    match = _UPTIME_RE.match(raw)
    if match is None:
        raise ValueError(f"invalid uptime string: {raw!r}")
    days, hours, minutes = (int(g) for g in match.groups())
    return timedelta(days=days, hours=hours, minutes=minutes)


def parse_epoch_seconds(value: int | float | None) -> datetime | None:
    """Convert a Unix epoch (seconds) into a UTC `datetime`.

    The Violet controller emits ``0`` for ``*_LAST_ON``/``*_LAST_OFF`` fields
    that have never fired, so ``0`` maps to ``None`` here.
    """
    if value is None or value == 0:
        return None
    if value < 0:
        raise ValueError(f"negative epoch seconds: {value}")
    return datetime.fromtimestamp(value, tz=UTC)


def parse_epoch_milliseconds(value: int | float | None) -> datetime | None:
    """Convert a Unix epoch (milliseconds) into a UTC `datetime`.

    Used by ``DOS_*_LAST_CAN_RESET`` fields.
    """
    if value is None or value == 0:
        return None
    if value < 0:
        raise ValueError(f"negative epoch milliseconds: {value}")
    return datetime.fromtimestamp(value / 1000.0, tz=UTC)


def parse_optional_seconds(value: float | int | str | None) -> timedelta | None:
    """Parse a duration-in-seconds value with a ``"NONE"`` sentinel.

    Used by ``HEATER_POSTRUN_TIME``: a float number of seconds while the
    timer runs, or the literal string ``"NONE"`` once it has expired.
    """
    if value is None or value == "NONE":
        return None
    return timedelta(seconds=float(value))

"""System-info typed view: firmware, uptime, CPU temps, memory."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from ..parsers import parse_epoch_seconds, parse_uptime_string


@dataclass(frozen=True, slots=True)
class SystemInfo:
    """Top-level system metadata from `/getReadings`.

    Covers the spec's "System informations" section plus a few undocumented
    extras the live demo controller emits (`HW_*_CARRIER`, `MEMORY_USED`,
    `CURRENT_TIME_UNIX`).
    """

    date: str
    time: str
    cpu_temp: float
    cpu_temp_carrier: float
    uptime: timedelta
    system_memory_mb: float
    sw_version: str
    sw_version_carrier: str
    hw_version_carrier: str | None = None
    hw_serial_carrier: str | None = None
    current_time: datetime | None = None

    @classmethod
    def from_raw(cls, raw: dict[str, Any]) -> SystemInfo:
        return cls(
            date=str(raw.get("date", "")),
            time=str(raw.get("time", "")),
            cpu_temp=float(raw.get("CPU_TEMP", 0.0)),
            cpu_temp_carrier=float(raw.get("CPU_TEMP_CARRIER", 0.0)),
            uptime=parse_uptime_string(raw.get("CPU_UPTIME", "0d 0h 0m")),
            system_memory_mb=float(raw.get("SYSTEM_MEMORY", 0.0)),
            sw_version=str(raw.get("SW_VERSION", "")),
            sw_version_carrier=str(raw.get("SW_VERSION_CARRIER", "")),
            hw_version_carrier=_maybe_str(raw.get("HW_VERSION_CARRIER")),
            hw_serial_carrier=_maybe_str(raw.get("HW_SERIAL_CARRIER")),
            current_time=parse_epoch_seconds(raw.get("CURRENT_TIME_UNIX")),
        )


def _maybe_str(value: Any) -> str | None:
    return None if value is None else str(value)

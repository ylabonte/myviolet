"""Tests for myviolet.models.system."""

from __future__ import annotations

from datetime import timedelta

from myviolet.models.system import SystemInfo


def test_from_raw_minimal() -> None:
    raw = {
        "date": "11.05.2026",
        "time": "12:07:09",
        "CPU_TEMP": 48.2,
        "CPU_TEMP_CARRIER": 38.2,
        "CPU_UPTIME": "250d 20h 24m",
        "SYSTEM_MEMORY": 175.2,
        "SW_VERSION": "1.1.9",
        "SW_VERSION_CARRIER": "1.0.1",
    }
    info = SystemInfo.from_raw(raw)
    assert info.date == "11.05.2026"
    assert info.time == "12:07:09"
    assert info.cpu_temp == 48.2
    assert info.cpu_temp_carrier == 38.2
    assert info.uptime == timedelta(days=250, hours=20, minutes=24)
    assert info.system_memory_mb == 175.2
    assert info.sw_version == "1.1.9"
    assert info.sw_version_carrier == "1.0.1"


def test_from_raw_with_extras(get_readings_seed: dict) -> None:
    """The live demo response should populate every documented field."""
    info = SystemInfo.from_raw(get_readings_seed)
    assert info.sw_version == "1.1.9"
    assert info.cpu_temp == 48.2
    assert info.uptime.days == 250
    assert info.hw_version_carrier == "1.0.0"
    assert info.hw_serial_carrier == "4"

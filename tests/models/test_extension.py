"""Tests for myviolet.models.extension."""

from __future__ import annotations

from datetime import timedelta

from myviolet.models.extension import ExtensionRelay, collect_extension_relays


def test_collect_both_buses(get_readings_seed: dict) -> None:
    buses = collect_extension_relays(get_readings_seed)
    assert set(buses.keys()) == {1, 2}
    assert len(buses[1]) == 8
    assert len(buses[2]) == 8

    relay_1_3 = buses[1][3]
    assert isinstance(relay_1_3, ExtensionRelay)
    assert relay_1_3.bus == 1
    assert relay_1_3.index == 3
    assert relay_1_3.runtime == timedelta(minutes=59, seconds=58)


def test_collect_skips_absent() -> None:
    raw = {"EXT1_1": 0, "EXT1_1_RUNTIME": "00h 00m 00s"}
    buses = collect_extension_relays(raw)
    assert buses == {1: {1: buses[1][1]}}

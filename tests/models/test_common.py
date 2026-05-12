"""Tests for myviolet.models._common."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from myviolet.enums import OutputState
from myviolet.models._common import MeasuredValue, OutputBase


class TestMeasuredValue:
    def test_from_raw_with_all_siblings(self) -> None:
        raw = {"pH_value": 7.3, "pH_value_min": 7.0, "pH_value_max": 7.5}
        mv = MeasuredValue.from_raw(raw, "pH", unit="pH")
        assert mv is not None
        assert mv.value == 7.3
        assert mv.unit == "pH"
        assert mv.min == 7.0
        assert mv.max == 7.5

    def test_from_raw_without_min_max(self) -> None:
        mv = MeasuredValue.from_raw({"pH_value": 7.3}, "pH", unit="pH")
        assert mv is not None
        assert mv.value == 7.3
        assert mv.min is None
        assert mv.max is None

    def test_from_raw_returns_none_when_value_missing(self) -> None:
        assert MeasuredValue.from_raw({}, "pH", unit="pH") is None


class TestOutputBase:
    def test_from_raw_complete(self) -> None:
        raw = {
            "PUMP": 1,
            "PUMP_LAST_ON": 1778500800,
            "PUMP_LAST_OFF": 1778500380,
            "PUMP_RUNTIME": "08h 24m 43s",
        }
        ob = OutputBase.from_raw(raw, "PUMP")
        assert ob is not None
        assert ob.state is OutputState.AUTO_ON
        assert ob.last_on == datetime(2026, 5, 11, 12, 0, 0, tzinfo=UTC)
        assert ob.last_off == datetime(2026, 5, 11, 11, 53, 0, tzinfo=UTC)
        assert ob.runtime == timedelta(hours=8, minutes=24, seconds=43)

    def test_from_raw_zero_epoch_means_never(self) -> None:
        raw = {
            "HEATER": 0,
            "HEATER_LAST_ON": 0,
            "HEATER_LAST_OFF": 0,
            "HEATER_RUNTIME": "00h 00m 00s",
        }
        ob = OutputBase.from_raw(raw, "HEATER")
        assert ob is not None
        assert ob.last_on is None
        assert ob.last_off is None
        assert ob.runtime == timedelta()

    def test_from_raw_missing_state_returns_none(self) -> None:
        """If the canonical key isn't present, the output isn't installed."""
        assert OutputBase.from_raw({}, "FOO") is None

    def test_state_helpers_work(self) -> None:
        raw = {"PUMP": 4, "PUMP_RUNTIME": "00h 00m 00s"}
        ob = OutputBase.from_raw(raw, "PUMP")
        assert ob is not None
        assert ob.state.is_manual
        assert ob.state.is_on

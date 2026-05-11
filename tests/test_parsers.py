"""Tests for myviolet.parsers — runtime/uptime strings and Unix epochs."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from myviolet.parsers import (
    parse_epoch_milliseconds,
    parse_epoch_seconds,
    parse_hms_string,
    parse_optional_seconds,
    parse_runtime_string,
    parse_uptime_string,
)


class TestParseRuntimeString:
    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("04h 33m 12s", timedelta(hours=4, minutes=33, seconds=12)),
            ("00h 00m 00s", timedelta()),
            ("08h 24m 43s", timedelta(hours=8, minutes=24, seconds=43)),
            ("23h 59m 59s", timedelta(hours=23, minutes=59, seconds=59)),
        ],
    )
    def test_valid(self, raw: str, expected: timedelta) -> None:
        assert parse_runtime_string(raw) == expected

    def test_with_extra_whitespace(self) -> None:
        assert parse_runtime_string("  04h 33m 12s  ") == timedelta(hours=4, minutes=33, seconds=12)

    def test_invalid_format_raises(self) -> None:
        with pytest.raises(ValueError, match="runtime"):
            parse_runtime_string("not-a-runtime")

    def test_empty_string_raises(self) -> None:
        with pytest.raises(ValueError):
            parse_runtime_string("")


class TestParseHmsString:
    """The older `HH:MM:SS` format used by PUMP_RPM_*_LAST_ON/OFF fields."""

    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("00:00:00", timedelta()),
            ("01:30:45", timedelta(hours=1, minutes=30, seconds=45)),
        ],
    )
    def test_valid(self, raw: str, expected: timedelta) -> None:
        assert parse_hms_string(raw) == expected

    def test_invalid_format_raises(self) -> None:
        with pytest.raises(ValueError):
            parse_hms_string("nope")


class TestParseUptimeString:
    """CPU_UPTIME is delivered as `Xd Yh Zm` (days/hours/minutes, no seconds)."""

    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("250d 11h 48m", timedelta(days=250, hours=11, minutes=48)),
            ("0d 0h 0m", timedelta()),
            ("1d 2h 3m", timedelta(days=1, hours=2, minutes=3)),
        ],
    )
    def test_valid(self, raw: str, expected: timedelta) -> None:
        assert parse_uptime_string(raw) == expected

    def test_invalid_format_raises(self) -> None:
        with pytest.raises(ValueError):
            parse_uptime_string("12:00:00")


class TestParseEpochSeconds:
    def test_valid_int(self) -> None:
        assert parse_epoch_seconds(1778500800) == datetime(2026, 5, 11, 12, 0, 0, tzinfo=UTC)

    def test_zero_is_none(self) -> None:
        # Many _LAST_OFF/_LAST_ON fields default to 0 meaning "never".
        assert parse_epoch_seconds(0) is None

    def test_none_passthrough(self) -> None:
        assert parse_epoch_seconds(None) is None

    def test_negative_raises(self) -> None:
        with pytest.raises(ValueError):
            parse_epoch_seconds(-1)


class TestParseEpochMilliseconds:
    def test_valid_int(self) -> None:
        # DOS_*_LAST_CAN_RESET is documented as Unix epoch (milliseconds).
        result = parse_epoch_milliseconds(1778500800000)
        assert result == datetime(2026, 5, 11, 12, 0, 0, tzinfo=UTC)

    def test_zero_is_none(self) -> None:
        assert parse_epoch_milliseconds(0) is None

    def test_none_passthrough(self) -> None:
        assert parse_epoch_milliseconds(None) is None


class TestParseOptionalSeconds:
    """HEATER_POSTRUN_TIME yields a float seconds value, or 'NONE' when up."""

    def test_float(self) -> None:
        assert parse_optional_seconds(120.5) == timedelta(seconds=120.5)

    def test_int(self) -> None:
        assert parse_optional_seconds(30) == timedelta(seconds=30)

    def test_none_sentinel(self) -> None:
        assert parse_optional_seconds("NONE") is None

    def test_none_value(self) -> None:
        assert parse_optional_seconds(None) is None

"""Tests for shared enums in myviolet.enums."""

from __future__ import annotations

import pytest

from myviolet.enums import (
    CoverState,
    DmxSceneState,
    DosingType,
    OnewireState,
    OutputState,
    PvSurplusState,
    RuleState,
    SimpleOnOff,
    YesNo,
)


class TestOutputState:
    def test_documented_values(self) -> None:
        assert OutputState.AUTO_OFF == 0
        assert OutputState.AUTO_ON == 1
        assert OutputState.AUTO_PRIO_OFF == 2
        assert OutputState.AUTO_PRIO_ON == 3
        assert OutputState.MANUAL_ON == 4
        assert OutputState.EMERGENCY_OFF == 5
        assert OutputState.MANUAL_OFF == 6

    @pytest.mark.parametrize(
        ("state", "is_on"),
        [
            (OutputState.AUTO_OFF, False),
            (OutputState.AUTO_ON, True),
            (OutputState.AUTO_PRIO_OFF, False),
            (OutputState.AUTO_PRIO_ON, True),
            (OutputState.MANUAL_ON, True),
            (OutputState.EMERGENCY_OFF, False),
            (OutputState.MANUAL_OFF, False),
        ],
    )
    def test_is_on(self, state: OutputState, is_on: bool) -> None:
        assert state.is_on is is_on

    @pytest.mark.parametrize(
        ("state", "is_manual"),
        [
            (OutputState.AUTO_OFF, False),
            (OutputState.AUTO_ON, False),
            (OutputState.AUTO_PRIO_OFF, False),
            (OutputState.AUTO_PRIO_ON, False),
            (OutputState.MANUAL_ON, True),
            (OutputState.EMERGENCY_OFF, False),
            (OutputState.MANUAL_OFF, True),
        ],
    )
    def test_is_manual(self, state: OutputState, is_manual: bool) -> None:
        assert state.is_manual is is_manual

    @pytest.mark.parametrize(
        ("state", "is_emergency"),
        [
            (OutputState.AUTO_PRIO_OFF, True),
            (OutputState.AUTO_PRIO_ON, True),
            (OutputState.EMERGENCY_OFF, True),
            (OutputState.AUTO_OFF, False),
            (OutputState.AUTO_ON, False),
            (OutputState.MANUAL_ON, False),
            (OutputState.MANUAL_OFF, False),
        ],
    )
    def test_is_emergency(self, state: OutputState, is_emergency: bool) -> None:
        assert state.is_emergency is is_emergency

    def test_constructible_from_int(self) -> None:
        assert OutputState(1) is OutputState.AUTO_ON

    def test_unknown_int_raises(self) -> None:
        with pytest.raises(ValueError):
            OutputState(99)


class TestDmxSceneState:
    def test_subset_of_output_state(self) -> None:
        assert DmxSceneState.AUTO_OFF == 0
        assert DmxSceneState.AUTO_ON == 1
        assert DmxSceneState.MANUAL_ON == 4
        assert DmxSceneState.MANUAL_OFF == 6

    def test_value_2_not_a_member(self) -> None:
        with pytest.raises(ValueError):
            DmxSceneState(2)


class TestRuleState:
    def test_documented_values(self) -> None:
        assert RuleState.INACTIVE == 0
        assert RuleState.ACTIVE == 1
        assert RuleState.BLOCKED_BY_RULE == 5
        assert RuleState.BLOCKED_MANUALLY == 6


class TestCoverState:
    def test_str_enum_values(self) -> None:
        assert CoverState.OPEN == "OPEN"
        assert CoverState.CLOSED == "CLOSED"
        assert CoverState.OPENING == "OPENING"
        assert CoverState.CLOSING == "CLOSING"
        assert CoverState.STOPPED == "STOPPED"

    def test_constructible_from_string(self) -> None:
        assert CoverState("OPEN") is CoverState.OPEN

    def test_unknown_string_raises(self) -> None:
        with pytest.raises(ValueError):
            CoverState("AJAR")


class TestOnewireState:
    def test_documented_values(self) -> None:
        assert OnewireState.OK == "OK"
        assert OnewireState.CRC_FAULT == "CRC_FAULT"
        assert OnewireState.DATA_MISSMATCH == "DATA_MISSMATCH"
        assert OnewireState.NOT_CONNECTED == "NOT_CONNECTED"
        assert OnewireState.NO_SENSOR_CONFIGURED == "NO_SENSOR_CONFIGURED"


class TestSimpleOnOff:
    def test_values(self) -> None:
        assert SimpleOnOff.ON == "ON"
        assert SimpleOnOff.OFF == "OFF"


class TestYesNo:
    def test_values(self) -> None:
        assert YesNo.YES == "YES"
        assert YesNo.NO == "NO"


class TestDosingType:
    def test_values(self) -> None:
        assert DosingType.ORP_ONLY == 0
        assert DosingType.ORP_AND_CL == 1


class TestPvSurplusState:
    def test_values(self) -> None:
        assert PvSurplusState.OFF == 0
        assert PvSurplusState.ON_BY_INPUT == 1
        assert PvSurplusState.ON_BY_HTTP == 2

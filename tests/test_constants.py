"""Tests for myviolet.constants — endpoint paths and control vocabularies."""

from __future__ import annotations

from myviolet import constants


def test_endpoint_paths() -> None:
    assert constants.PATH_GET_READINGS == "/getReadings"
    assert constants.PATH_GET_CONFIG == "/getConfig"
    assert constants.PATH_SET_FUNCTION_MANUALLY == "/setFunctionManually"
    assert constants.PATH_SET_TARGET_VALUES == "/setTargetValues"
    assert constants.PATH_SET_CONFIG == "/setConfig"
    assert constants.PATH_SET_DOSING_PARAMETERS == "/setDosingParameters"


def test_readings_keywords() -> None:
    assert "ALL" in constants.READINGS_KEYWORDS
    assert "DOSAGE" in constants.READINGS_KEYWORDS
    assert "RUNTIMES" in constants.READINGS_KEYWORDS


def test_default_readings_query() -> None:
    """Default fetch should request everything available."""
    assert constants.DEFAULT_READINGS_QUERY == "ALL,DOSAGE,RUNTIMES"


def test_actions_include_basic_set() -> None:
    for action in ("ON", "OFF", "AUTO"):
        assert action in constants.CONTROL_ACTIONS


def test_dosing_codes() -> None:
    assert set(constants.DOSING_CODES) == {"CL", "ELO", "ELO_REV", "PHM", "PHP", "FLOC"}


def test_target_value_ranges() -> None:
    """Setpoint ranges from the vendor manual."""
    assert constants.SETPOINT_RANGES["pH"] == (6.8, 7.8)
    assert constants.SETPOINT_RANGES["ORP"] == (600, 800)
    assert constants.SETPOINT_RANGES["MinChlorine"] == (0.2, 2.0)
    assert constants.SETPOINT_RANGES["Heater"] == (20.0, 35.0)
    assert constants.SETPOINT_RANGES["Solar"] == (20.0, 40.0)

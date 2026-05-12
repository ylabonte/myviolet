"""Endpoint paths, action vocabularies, and setpoint ranges.

This module is the source of truth for any literal string that travels in
or out of the Violet HTTP API. Reused by `transport`, `client`, and the
mock service so paths can never diverge.
"""

from __future__ import annotations

from typing import Final

# Read endpoints
PATH_GET_READINGS: Final[str] = "/getReadings"
PATH_GET_CONFIG: Final[str] = "/getConfig"
PATH_GET_HISTORY: Final[str] = "/getHistory"
PATH_GET_WEATHER: Final[str] = "/getWeatherData"
PATH_GET_OVERALL_DOSING: Final[str] = "/getOverallDosing"
PATH_GET_OUTPUT_STATES: Final[str] = "/getOutputStates"
PATH_GET_CALIBRATION_RAW: Final[str] = "/getCalibrationRawValues"
PATH_GET_CALIBRATION_HISTORY: Final[str] = "/getCalibrationHistory"

# Write endpoints
PATH_SET_FUNCTION_MANUALLY: Final[str] = "/setFunctionManually"
PATH_SET_TARGET_VALUES: Final[str] = "/setTargetValues"
PATH_SET_CONFIG: Final[str] = "/setConfig"
PATH_SET_DOSING_PARAMETERS: Final[str] = "/setDosingParameters"
PATH_SET_OUTPUT_TEST_MODE: Final[str] = "/setOutputTestMode"
PATH_RESTORE_CALIBRATION: Final[str] = "/restoreCalibration"

# /getReadings query keywords
READINGS_KEYWORDS: Final[frozenset[str]] = frozenset({"ALL", "DOSAGE", "RUNTIMES"})
DEFAULT_READINGS_QUERY: Final[str] = "ALL,DOSAGE,RUNTIMES"

# Action vocabulary for /setFunctionManually
CONTROL_ACTIONS: Final[frozenset[str]] = frozenset(
    {
        "ON",
        "OFF",
        "AUTO",
        "PUSH",
        "COLOR",
        "LOCK",
        "UNLOCK",
        "ALLON",
        "ALLOFF",
        "ALLAUTO",
    }
)

# Cover-control keys (gated by acknowledge_unsafe=True for OPEN/CLOSE)
CONTROL_KEY_COVER_OPEN: Final[str] = "COVER_OPEN"
CONTROL_KEY_COVER_CLOSE: Final[str] = "COVER_CLOSE"
CONTROL_KEY_COVER_STOP: Final[str] = "COVER_STOP"
UNSAFE_COVER_KEYS: Final[frozenset[str]] = frozenset(
    {CONTROL_KEY_COVER_OPEN, CONTROL_KEY_COVER_CLOSE}
)

# Channel numbers and codes for /DOS_* fields and dosing controls
DOSING_CHANNELS: Final[dict[int, str]] = {
    1: "CL",
    2: "ELO",
    3: "ELO_REV",
    4: "PHM",
    5: "PHP",
    6: "FLOC",
}
DOSING_CODES: Final[frozenset[str]] = frozenset(DOSING_CHANNELS.values())

# Setpoint ranges accepted by /setTargetValues (vendor manual).
# Tuples are (low, high), inclusive.
SETPOINT_RANGES: Final[dict[str, tuple[float, float]]] = {
    "pH": (6.8, 7.8),
    "ORP": (600, 800),
    "MinChlorine": (0.2, 2.0),
    "Heater": (20.0, 35.0),
    "Solar": (20.0, 40.0),
}

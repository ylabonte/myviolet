"""Shared enums for fields returned by the Violet controller API.

Each enum mirrors a documented value table from the vendor's `getReadings.xlsx`
specification. The `OutputState` enum is reused across ~30 binary outputs
(pump, heater, solar, light, refill, eco, backwash, backwash rinse, all dosing
channels, and all extension relays).
"""

from __future__ import annotations

from enum import IntEnum, StrEnum


class OutputState(IntEnum):
    """State of any binary output controlled by the Violet controller.

    These seven values are emitted by every relay-style output: pump, heater,
    solar, light, refill, eco, backwash, backwash rinse, the five dosing
    channels, and both extension relay buses.
    """

    AUTO_OFF = 0
    AUTO_ON = 1
    AUTO_PRIO_OFF = 2
    AUTO_PRIO_ON = 3
    MANUAL_ON = 4
    EMERGENCY_OFF = 5
    MANUAL_OFF = 6

    @property
    def is_on(self) -> bool:
        """Whether the output is currently energised, regardless of cause."""
        return self in (OutputState.AUTO_ON, OutputState.AUTO_PRIO_ON, OutputState.MANUAL_ON)

    @property
    def is_manual(self) -> bool:
        """Whether the output is in a user-forced (manual) state."""
        return self in (OutputState.MANUAL_ON, OutputState.MANUAL_OFF)

    @property
    def is_emergency(self) -> bool:
        """Whether an emergency or priority rule is currently in effect."""
        return self in (
            OutputState.AUTO_PRIO_OFF,
            OutputState.AUTO_PRIO_ON,
            OutputState.EMERGENCY_OFF,
        )


class DmxSceneState(IntEnum):
    """State of a DMX scene. Subset of `OutputState` (no priority rules)."""

    AUTO_OFF = 0
    AUTO_ON = 1
    MANUAL_ON = 4
    MANUAL_OFF = 6


class RuleState(IntEnum):
    """State of a digital-input switching rule."""

    INACTIVE = 0
    ACTIVE = 1
    BLOCKED_BY_RULE = 5
    BLOCKED_MANUALLY = 6


class CoverState(StrEnum):
    """Position / motion state of the pool cover."""

    OPEN = "OPEN"
    CLOSED = "CLOSED"
    OPENING = "OPENING"
    CLOSING = "CLOSING"
    STOPPED = "STOPPED"


class OnewireState(StrEnum):
    """Fault state of a 1-wire temperature sensor.

    Note: ``DATA_MISSMATCH`` (sic) is spelled with two ``s`` letters to match
    the wire value emitted verbatim by the controller firmware.
    """

    OK = "OK"
    CRC_FAULT = "CRC_FAULT"
    DATA_MISSMATCH = "DATA_MISSMATCH"
    NOT_CONNECTED = "NOT_CONNECTED"
    NO_SENSOR_CONFIGURED = "NO_SENSOR_CONFIGURED"


class SimpleOnOff(StrEnum):
    """Binary on/off used by overflow and bathing-AI flags."""

    ON = "ON"
    OFF = "OFF"


class YesNo(StrEnum):
    """Binary yes/no used by various status flags."""

    YES = "YES"
    NO = "NO"


class DosingType(IntEnum):
    """Configuration of a chlorine dosing controller."""

    ORP_ONLY = 0
    ORP_AND_CL = 1


class PvSurplusState(IntEnum):
    """Trigger source of the PV surplus function."""

    OFF = 0
    ON_BY_INPUT = 1
    ON_BY_HTTP = 2

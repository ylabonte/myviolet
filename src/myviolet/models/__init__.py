"""Typed views over the raw `/getReadings` JSON dict.

Each submodule covers one category from the official `getReadings.xlsx`
field spec. Views are constructed by `myviolet.readings.VioletReadings`
from the raw dict and exposed as lazy memoized properties. Every public
class re-exported here is also re-exported at the top level (`myviolet.X`)
to make the supported public API obvious to consumers and to semver tooling.
"""

from ._common import MeasuredValue, OutputBase
from .chemistry import WaterChemistry
from .cover import Cover
from .dmx import DmxScene
from .dosing import DosingChannel
from .extension import ExtensionRelay
from .inputs import CanEmptyInput, DigitalInput
from .outputs import (
    Backwash,
    BackwashRinse,
    Eco,
    Heater,
    Light,
    Pump,
    PumpSpeed,
    Refill,
    Solar,
)
from .rules import SwitchingRule
from .sensors import AnalogSensor, ImpulseInput, OneWireSensor
from .system import SystemInfo
from .system_states import BackwashStatus, BathingAi, OverflowState, PvSurplus

__all__ = [
    "AnalogSensor",
    "Backwash",
    "BackwashRinse",
    "BackwashStatus",
    "BathingAi",
    "CanEmptyInput",
    "Cover",
    "DigitalInput",
    "DmxScene",
    "DosingChannel",
    "Eco",
    "ExtensionRelay",
    "Heater",
    "ImpulseInput",
    "Light",
    "MeasuredValue",
    "OneWireSensor",
    "OutputBase",
    "OverflowState",
    "Pump",
    "PumpSpeed",
    "PvSurplus",
    "Refill",
    "Solar",
    "SwitchingRule",
    "SystemInfo",
    "WaterChemistry",
]

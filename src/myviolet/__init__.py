"""Async Python library for the Pooldigital Violet pool controller."""

try:
    from ._version import __version__
except ImportError:  # pragma: no cover
    from importlib.metadata import PackageNotFoundError, version

    try:
        __version__ = version("myviolet")
    except PackageNotFoundError:
        __version__ = "0.0.0.dev0"

from .client import VioletClient
from .enums import (
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
from .exceptions import (
    BadCredentialsException,
    BadStatusCodeException,
    InvalidPayloadException,
    SetpointValidationError,
    TimeoutException,
    UnsafeOperationException,
    VioletApiException,
)
from .hardware import HardwareProfile
from .models import (
    BackwashStatus,
    BathingAi,
    Cover,
    DmxScene,
    DosingChannel,
    ExtensionRelay,
    Heater,
    MeasuredValue,
    OneWireSensor,
    OutputBase,
    OverflowState,
    Pump,
    PumpSpeed,
    PvSurplus,
    SystemInfo,
    WaterChemistry,
)
from .readings import VioletReadings

__all__ = [
    "__version__",
    "BackwashStatus",
    "BadCredentialsException",
    "BadStatusCodeException",
    "BathingAi",
    "Cover",
    "CoverState",
    "DmxScene",
    "DmxSceneState",
    "DosingChannel",
    "DosingType",
    "ExtensionRelay",
    "HardwareProfile",
    "Heater",
    "InvalidPayloadException",
    "MeasuredValue",
    "OneWireSensor",
    "OnewireState",
    "OutputBase",
    "OutputState",
    "OverflowState",
    "Pump",
    "PumpSpeed",
    "PvSurplus",
    "PvSurplusState",
    "RuleState",
    "SetpointValidationError",
    "SimpleOnOff",
    "SystemInfo",
    "TimeoutException",
    "UnsafeOperationException",
    "VioletApiException",
    "VioletClient",
    "VioletReadings",
    "WaterChemistry",
    "YesNo",
]
